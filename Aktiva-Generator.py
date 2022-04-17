import ipaddress
import webbrowser
from msilib.schema import CheckBox
from tkinter import END, W, E, S, IntVar, Label, StringVar, Tk, mainloop, Radiobutton, Button, Entry, PhotoImage, messagebox
import re
from tkinter.scrolledtext import ScrolledText


main = Tk()
main.title('Aktiva Generator')

variable=IntVar()


def write():
    outBox.delete(1.0, END)

    host = field1.get().upper()
    host=re.findall("[A-Z0-9]{4,20}",host)
    if (host[0]=="MZOS"):
        host=host[1]
    else:
        host=host[0]
    slash="/" + fieldSlash.get()
    
    

    range = ipaddress.IPv4Address(field2.get())


    if host and range and var.get()==1:
        Ans = ("/interface bridge port set bridge=BD-"+ host + "-javne [find where interface=Gi1/4]\n\n"
        "/interface ethernet set [find default-name=ether4] comment=\"Access_eSkoleUTM\" \n\n"
        "/ip dhcp-server option\n"
        "add code=240 name=FortiPrimar value=\"\'193.198.252.16\'\" \n"
        "add code=43 name=Cisco value=\"\'\\\"5A1N;B2;K4;I193.198.252.10;J80\\\"\'\" \n"
        "add code=240 name=FortiBackup value=\"\'193.198.252.17\'\" \n\n"
        "/ip dhcp-server network add address=" + str(range) + slash + " dhcp-option=Cisco,FortiPrimar,FortiBackup dns-server=193.198.184.130,193.198.184.140 gateway=" + str(range+1) + "\n"
        "/ip pool add name=Javni-pool ranges="+ str(range+3) +"\n"
        "/ip dhcp-server add address-pool=Javni-pool disabled=no interface=BD-" + host + "-javne lease-time=1d10m name=Javni_DHCP \n\n"
        "/ip route add distance=1 dst-address=" + str(range+4) + "/30 gateway=" + str(range+3) + "\n\n\n\n"
        )
   
        outBox.insert(1.0, Ans)

    elif host and range and var.get()==2:
        Ans = ("/ip firewall filter\n"
        "remove [find where dynamic=no]\n"
        "add action=drop chain=input port=8291 protocol=tcp src-address-list=!PL-CARNet\n"
        "add chain=forward in-interface=BD-" + host + "-javne action=jump jump-target=prema_jezgri11\n"
        "add chain=prema_jezgri11 action=drop protocol=tcp port=135,139,445\n"
        "add chain=prema_jezgri11 action=drop protocol=udp port=17,19,135,137,138,1900\n"
        "add chain=prema_jezgri11 action=drop protocol=tcp src-address-list=PL-" + host + " dst-address-list=PL-privatne\n"
        "add chain=prema_jezgri11 action=drop protocol=udp src-address-list=PL-" + host + " dst-address-list=PL-privatne\n"
        "add chain=prema_jezgri11 action=drop protocol=icmp src-address-list=PL-" + host + " dst-address-list=PL-privatne\n"
        "add chain=prema_jezgri11 action=accept src-address-list=PL-" + host + " dst-address=0.0.0.0/0\n"
        "add chain=prema_jezgri11 action=drop src-address=0.0.0.0/0 dst-address=0.0.0.0/0\n\n"

        "/ip firewall address-list\n"
        "remove [find]\n"
        "add address=161.53.12.0/24 list=PL-CARNet\n"
        "add address=193.198.220.64/26 list=PL-CARNet\n"
        "add address=161.53.178.142/32 list=PL-CARNet\n"
        "add address=172.17.128.0/26 list=PL-CARNet\n"
        "add address=10.0.0.0/8 list=PL-privatne\n"
        "add address=172.16.0.0/12 list=PL-privatne\n"
        "add address=192.168.0.0/16 list=PL-privatne\n"
        "add address=" + str(range) + slash + " list=PL-" + host + "\n\n\n"
        "/interface ethernet set [find where name!=\"Gi0/1\" && name!=\"Gi1/1\" && name!=\"Gi1/4\" && running=no] disabled=yes\n"
        )
        outBox.insert(1.0, Ans)

    elif host and range and var.get()==3:
        Ans =("/interface bridge port set bridge=BD-"+ host + "-javne [find where interface=Gi1/4]\n\n"
        "/interface ethernet set [find default-name=ether4] comment=\"Access_eSkoleUTM\" \n\n"
        "/ip dhcp-server network add address=" + str(range) + slash + " dns-server=193.198.184.130,193.198.184.140 gateway=" + str(range+1) + "\n"
        "/ip pool add name=Javni-pool ranges="+ str(range+3) +"\n"
        "/ip dhcp-server add address-pool=Javni-pool disabled=no interface=BD-" + host + "-javne lease-time=1d10m name=Javni_DHCP \n\n"
        "/ip firewall nat set [find where chain=srcnat] to-address=" + str(range+6)+"\n")
        outBox.insert(1.0, Ans)

    else:
        msgBox()

##############UNDER CONSTRUCTION#################

def sendMail():
    if(field3.get()):

        #zastavica promjene konfiguracije
        flagInic=0
        recipient = 'rt+mreza-eskole@tt.carnet.hr'
        subject, allIP, vlanID = titleGen()

        #Provjera promjene PtP adrese
        if allIP[0]==allIP[1]:
            body=allIP[1] + '/30'
        else:
            body=allIP[0] + '/30 -> ' + allIP[1]+'/30'
            flagInic=1
        
        #Provjera promjene javne adrese
        if allIP[2]==allIP[3]:
            body=body + '%0D%0A' + allIP[3]
        else:
            body=body + '%0D%0A' + allIP[2] + ' -> ' + allIP[3]
            flagInic=1
        
        #Provjera promjene Vlan ID-a
        if vlanID[2]==vlanID[3]:
            body=body + '%0D%0A' + vlanID[-1]
        else:
            body=body + '%0D%0A' + vlanID[-2] + ' -> ' + vlanID[-1]
            flagInic=1
        
        body=body + '%0D%0A%0D%0A**** TODO ****'
        

        webbrowser.open('mailto:?to=' + recipient + '&subject=' + subject + '&body=' + body, new=1)
    
    else:
     msgBox()

##################################################




def msgBox():
    #messagebox.showerror('error', 'Unesi hostname i javni raspon adresa')
    messagebox.showwarning('warning', 'Nisu odabrana/unesena sva polja')


def clear():
    field1.delete(0, END)
    field2.delete(0, END)
    outBox.delete(1.0, END)
    fieldSlash.setvar("29")


def titleGen():
    titleField=field3.get().upper()

    tehnologijaSpajanja=['DSL','GSM','HIBRID']

    # RE za IPv4 adrese, subnet, hostname, naziv ustanove i adresu, vlan id
    allIP = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",titleField)
    hostName=re.findall(r"\bMZOS-[\w-]+-1\b", titleField)[1]
    nazivAdresa= str(re.search(r"([A-Z]{1})(.{20,100})\d{5}",titleField).group()) + ' '
    vlanID=re.findall(r"\b\d{4}\b",titleField)
    subnetIP=re.findall(r'[/]\d{2}',titleField)
    titleField=(titleField.split())
    idProjCN=titleField[0] + ' - ' + titleField[1] + ' - '

    #
    for i in range(len(allIP)):
        subnetIP[i]=allIP[i]+subnetIP[i]

    #provjera adrese na koju se spajamo ovisno o tehnologiji spajanja
    if any (i in titleField for i in tehnologijaSpajanja):
        adresaIP=ipaddress.IPv4Address(allIP[3])+2
    else:
        adresaIP=ipaddress.IPv4Address(allIP[3])+1

    #Generiranje naslova
    title=idProjCN + '[' + str(adresaIP) + '] - ' + nazivAdresa + ' ' + hostName + ' - rekonfiguracija'

    #zamjena whitespace-ova, tabova sa jednim whitespace-om
    title=re.sub(r'\s+','%20',title)

    return title, subnetIP, vlanID

#1015 - 1896 - [82.132.6.225] - OSNOVNA ŠKOLA RUDEŠJABLANSKA ULICA 51ZAGREB10000  OS-ZG-RUDES-1MZOS-OS-ZG-RUDES - rekonfiguracija


######TESTIRANJE#################################

#def setLabelRaspon():
#    if var.get()==1:
#        fieldSlash.config(text="/29")
#    else:
#        fieldSlash.config(text="")

##################################################




main.geometry('1100x540')

Label(main, text = "Hostname:").grid(row=0, column=1, sticky=W, pady=2, padx=255)
Label(main, text = "Javni range:").grid(row=1, column=1,sticky=W, pady=2, padx=255)
Label(main, text = "Mail(text):").grid(row=3, column=1,sticky=W, padx=255)
Label(main, text = "Mikrotik naredbe:",background='light grey').grid(row=3, column=1, sticky=W, padx=15)
Label(main, text="/").grid(row=1,column=1,sticky=E,padx=330)

#logoCarnet=PhotoImage(file="C:/Users/KrešimirŠodan/Downloads/carnetlogosmall2.png")
outBox = ScrolledText(main, height=23, width=111, pady=20)
field1 = Entry(main, width=40)
field2 = Entry(main, width=40)
field3 = Entry(main, width=40)
fieldSlash = Entry(main, width=2,fg='grey')
fieldSlash.insert(1 ,"29")
#labelRaspon = Label(main,text="")

#Logo
logoCarnetLabel=Label(main, text="CARNET", fg='grey')
logoCarnetLabel.grid(row=4,column=2,columnspan=2,sticky=S,pady=15)


outBox.grid(row=4, column=1, padx=10)
field1.grid(row=0, column=1, pady=2)
field2.grid(row=1, column=1, pady=2)
field3.grid(row=3, column=1, pady=2)
fieldSlash.grid(row=1, column=1, sticky=E, padx=316, pady=2)
#labelRaspon.grid(row=1,column=1,sticky=E, padx=295)


var=IntVar()
Radiobutton(main, text="Rekonfig", variable=var, value=1).grid(row=2,column=1, sticky=W, padx=265)
Radiobutton(main, text="Firewall", variable=var, value=2).grid(row=2,column=1, sticky=W, padx=345)
Radiobutton(main, text="G3Rekonfig", variable=var, value=3).grid(row=2,column=1)
Radiobutton(main, text="G3Firewall", variable=var, value=4).grid(row=2,column=1, sticky=E, padx=335)


Button(main, text='Očisti', command=clear, width=10).grid(row=1, column=2, sticky=W, padx=2, pady=2)
Button(main, text='Zatvori', command=main.destroy, width=10).grid(row=1, column=3, sticky=W, padx=2, pady=2)
Button(main, text='Ispiši', command=write, width=22).grid(row=0, column=2, columnspan=2, padx=2, pady=2)
Button(main, text="E-mail", command=sendMail, width=22).grid(row=2, column=2, columnspan=2, sticky=W, padx=2, pady=2)




mainloop()