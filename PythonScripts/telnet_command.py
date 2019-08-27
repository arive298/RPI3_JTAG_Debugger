import telnetlib

HOST = "localhost"
tn = telnetlib.Telnet(HOST,4444)

# This commands is used to read from registers and memory


# use to send a singe command withut paramteres
def send_telnet_command(cmd, param=0, speed=2):
   # print('writing to telnet server')
    if(param == 0):
        cmd = cmd+"\r\n"
    else:
        cmd = cmd+' '+param+"\r\n"
        
    cmd = cmd.encode('utf-8')
    tn.write(cmd)
    #print('reading from telnet server')
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

print(send_telnet_command("halt"))

sp = send_telnet_command("reg","90",0.1)
sp = get_stripped_reg(sp)
print("sp = "+str(sp))

addr = send_telnet_command("mdw",sp,0.1)
addr = get_stripped_address(addr)
print(sp+': '+addr)

send_telnet_command("resume")
#send_telnet_command("shutdown")


