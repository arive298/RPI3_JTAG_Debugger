import telnetlib

HOST = "localhost"
tn = telnetlib.Telnet(HOST,4444)
DEBUG_TELNET = False
DEBUG = False
# use to send a singe command withut paramteres
def send_telnet_command(cmd, param='', speed=2):
    if(DEBUG_TELNET):
       print('writing to telnet server')
    cmd = cmd+' '+param+"\r\n"
    cmd = cmd.encode('utf-8')
    tn.write(cmd)
    
    if(DEBUG_TELNET):
        print('reading from telnet server')
    
    ret = tn.read_until(b'jsfjjsd',speed)
    return ret.decode('utf-8')

#Stripp address from the obtained bytes of the telnet server    
def get_stripped_reg(reg):
    index = reg.find('0x')
    reg = reg[index:(index+10)]
    return reg

def get_stripped_address(address):
    index = address.find(':')
    index = index + 2
    address = address[index:(index+8)]
    return address

def get_stripped_name(address):
    index = address.find(':')
    index = index + 2
    name_in_hex = (address[index:]).replace(" ","").replace("00000000","").replace("\r","").replace("\n","").replace(">","")
    return name_in_hex

def change_endian(address):
    result = []
    for i in range(int(len(address)/8)):  
       start = 7+(i*8)
       for j in range(4):
           result.append(address[start-1:start+1])
           start-=2
    for i in range(len(result)):
        result[i] = int(result[i],16)
        
    string_result = ''.join(chr(i) for i in result)
    return string_result

def get_task_name(task_addr):
    task_addr = hex( int(task_addr,16) + int('0x4ac',16) )
    contents = get_stripped_name(send_telnet_command('mdw', (task_addr + " 4"), 0.1))
    endians = change_endian(contents)
    return endians

def get_first_task(address):
    bin_addr = hex( ((int(address,16)) & int('0xffffe000',16) ) + int('0xc',16)) 
    task = get_stripped_address( send_telnet_command('mdw', bin_addr, 0.1))
    task = hex(int(task,16))
    print(task)
    return task

def get_next_task(address):
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
    next_pointer = hex( (int(address,16))  + int('0x304',16))
    next_address = get_stripped_address( send_telnet_command('mdw', next_pointer, 0.1))
    next_task = hex( (int(next_address,16))  - int('0x300',16))
    return next_task

def find_tasks(task_name):
    print(send_telnet_command("halt"))
    sp = get_stripped_reg(send_telnet_command("reg","90",0.1))
    addr = get_stripped_address(send_telnet_command("mdw",sp,0.1))
    current_address = get_first_task(addr)
    
    current_name = get_task_name(current_address)
    first_proc_name = current_name
    if(DEBUG):
        print("First process name: "+first_proc_name)
    
    count = 0
    while (current_name != task_name and (task_name not in current_name) ):
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

addr = find_tasks("geany")
if(addr == "not found"):
    print("Task was not found or it does not exists")
else:
    print("task was found at address: "+addr)
send_telnet_command("resume")
#send_telnet_command("shutdown")


