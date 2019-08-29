import telnetlib
import sys

HOST = "localhost"
tn = telnetlib.Telnet(HOST,4444)
DEBUG_TELNET = False
DEBUG = True 

def send_telnet_command(cmd, param='', speed=2):
    """
    Used to send a telnet command to openocd
    :Param - cmd - Command to send
    :Param - param - Parameter for the openocd
    :Param - speed - To change time-out of the read function 
    :Return - the output of the sent command 
    """
    if(DEBUG_TELNET):
       print('writing to telnet server')
    cmd = cmd+' '+param+"\r\n"
    cmd = cmd.encode('utf-8')
    tn.write(cmd)
    
    if(DEBUG_TELNET):
        print('reading from telnet server')
    
    ret = tn.read_until(b'jsfjjsd',speed)
    return ret.decode('utf-8')

def get_stripped_reg(reg_contents):
    """
    Strip the obtained address from the register after getting string the telnet command "reg <reg # or name>     
    :Param - reg_contents - The contents of the register to strip
    :Returns - the string address
    """
    index = reg_contents.find('0x')
    addr = reg_contents[index:(index+10)]
    return addr

def get_stripped_address(address):
    """
    Function used to strip a specific address from the returned telnet command 
    :Param - adress - The starting address to strip the name
    :Returns - the string address
    """
    index = address.find(':')
    index = index + 2
    address = address[index:(index+8)]
    return address

def get_stripped_name(address):
    """
    Function used to get the stripped address of the task from the 'mdw' telnet command
    :Param - address- The starting address to strip the name
    :Returns - The hex string 
    """
    index = address.find(':')
    index = index + 2
    name_in_hex = (address[index:]).replace(" ","").replace("00000000","").replace("\r","").replace("\n","").replace(">","")
    # name_in_hex = (address[index:]).replace("\r","").replace("\n","").replace(">","")
    return name_in_hex

def change_endian(address):
    """
    Used to change the little endian format of string in RPI3 to readable format. (Note: it works only for dword)
    :Param - address The address to change endianes
    :Return - a hex list that can be later converted
    """
    result = []
    for i in range(int(len(address)/8)):  
       start = 7+(i*8)
       for j in range(4):
           result.append(address[start-1:start+1])
           start-=2
    for i in range(len(result)):
        result[i] = int(result[i],16)
        
    return result

def get_task_name(task_addr):
    """
    Function to get the decoded string name of a task from a given task address
    :Param - task_addr Address of task for which the name will be extracted
    :Return - the fully converted string
    """
    task_addr = hex( int(task_addr,16) + int('0x4ac',16) ) 
    contents = get_stripped_name(send_telnet_command('mdw', (task_addr + " 4"), 0.1))
    endians = change_endian(contents)
    index = len(endians)
    for i in range(len(endians)):
        if(endians[i] == 0):
            index = i
            break
    
    endians = endians[0:index]
    string_result = ''.join(chr(i) for i in endians)
    return string_result

def get_first_task(sp_contents):
    """
    This function is only used for obtaining the first task(currently running task) because it requires some specific calculations involving the stack pointer, 
    and the same math does not apply to the other tasks
    :Param - sp_contents The address obtained from sp 
    :Returns - the address of the first task(currently running task)
    """
    
    bin_addr = hex( ((int(sp_contents,16)) & int('0xffffe000',16) ) + int('0xc',16)) 
    task = get_stripped_address( send_telnet_command('mdw', bin_addr, 0.1))
    task = hex(int(task,16))
    print(task)
    return task

def get_next_task(address):
    """
    Gets the address in memory of the next task
    :Param - address of the current task
    :Return - the calculated address
    """
    next_pointer = hex( (int(address,16))  + int('0x300',16))
    next_address = get_stripped_address( send_telnet_command('mdw', next_pointer, 0.1))
    next_task = hex( (int(next_address,16))  - int('0x300',16))
    
    if(DEBUG):
        print("next_pointer: " + next_pointer)
        print("next_address: " + next_address)
        print("Next_task: "+next_task)
        content_of_next_task = send_telnet_command('mdw', next_task, 0.1)
        print("Contents of next_task: "+content_of_next_task)

    return next_task

def get_previous_task(address):
    """
    Gets the address in memory of the previous task
    :Param - address of the current task
    :Return - the calculated address
    """
    next_pointer = hex( (int(address,16))  + int('0x304',16))
    next_address = get_stripped_address( send_telnet_command('mdw', next_pointer, 0.1))
    next_task = hex( (int(next_address,16))  - int('0x300',16))
    return next_task

def find_tasks(task_name, loop_backward = True):
    """
    This function finds the address of a specific task. Thu function loop through the process list to find a matching name.
    you can ither loop foreward or backward by passing false as the second parameter
    :Param - task_name Name of the task to find
    :Param - loop_backward Looping direction, defaulted to backward
    :Return - the found address, other wise it returns 'not found'
    """
    halt_result = send_telnet_command("halt")
    
    if(DEBUG):
        print("Task to find: "+task_name)
        print(halt_result)

    sp = get_stripped_reg(send_telnet_command("reg","90",0.1))
    addr = get_stripped_address(send_telnet_command("mdw",sp,0.1))
    current_address = get_first_task(addr)
    
    current_name = get_task_name(current_address)
    first_proc_name = current_name
    
    if(DEBUG):
        print("First process name: "+first_proc_name)
    
    count = 0
    while (current_name != task_name ):
       
        if(loop_backward):
            current_address = get_previous_task(current_address)
        else:
            current_address = get_next_task(current_address)

        current_name = get_task_name(current_address)
       
        if(DEBUG):
            print("Current_address: "+current_address)
            print("Current_name: "+current_name)
        
        count += 1
        if(count == 1):
            first_proc_name = current_name

        if(count > 1 and first_proc_name == current_name):
            return "not found"
        
        

    return current_address



# sp = send_telnet_command("reg","90",0.1)
# sp = get_stripped_reg(sp)
# print("sp = "+str(sp))

# addr = send_telnet_command("mdw",sp,0.1)
# addr = get_stripped_address(addr)
# print(sp+': '+addr)

# first = get_first_task(addr)
# print("First addr: "+first )
# next = get_next_task(first)
# print("Next addr: "+next)

# get_task_name(next)

addr = find_tasks("openbox")
if(addr == "not found"):
    print("Task was not found or it does not exists")
else:
    print("task was found at address: "+addr)


send_telnet_command("resume")
# send_telnet_command("shutdown")


