Splunk

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.001.jpeg)

Setting up the Splunk Enterprises Server:

What Is VirtualBox?

VirtualBox is a software virtualization package that you can install on your operating system (just as you would a normal program). It supports the creation and management of virtual machines into which you can install a second operating system.

Install VirtualBox

The first thing to do is to get VirtualBox installed. I’ll not go into much detail here, as there are comprehensive instructions for all of the main operating systems [on the project’s homepage](https://www.virtualbox.org/wiki/Downloads).

Downloads Ubuntu Live Server from <https://ubuntu.com/download/server>

Create a New Virtual Machine

Start up VirtualBox. This should open the VirtualBox Manager, the interface from which you will administer all of your virtual machines.

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.002.jpeg)

Next Click on *New* (in the top right of the VirtualBox Manager), give your virtual machine a name and the two drop down menus should automatically update.

Click *Next*. The wizard will now ask you to select the amount of memory (RAM) in megabytes to be allocated to the virtual machine. I chose 2GB (2048 megabytes).

![ref1]

On the next screen you will be asked whether the new virtual hard disk should grow as it is used (dynamically allocated) or if it should be created at its maximum size. Make sure that *dynamically allocated* is selected, then click *Next*.

Finally, select the size of the virtual hard disk in megabytes. The default size of 10GB should be plenty, but feel free to increase this as you see fit. Then click *Create*.

I do Recommenend to allocate a storage of alteast 40GB for Splunk Enterprices Server Since it has to Store Logs and Data During Running Anlysis.

![ref1]

Setting Up a Virtual NAT Network for the Devices to Connect to a Router:

Create a NAT Network and Give it Some name in my Seinerio its "Project" with the IPv4 of 192.168.10.1/24 , Do enable DHCP and Save the NAT Network.

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.004.jpeg)

In the Setting of the Ubuntu Live Server , Go to networks and set the Adapter 1 to NAT Networks of the New Created network.

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.005.jpeg)

Fixing the IP Address of the Splunk Server to 192.168.10.10 Static :

ip a #For Checking the IP Addr of  the Linux Server ![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.006.png)

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.007.jpeg)

Making the IP Addresses Static for the Splunk Server to 192.168.10.10

sudo nano /etc/netplan/00-installer-config.yaml![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.008.png)

#config file![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.009.png)

network:

`   `ethernets:

`      `enp0s3:

`        `dhcp4: no

`        `addresses: [192.168.10.10/24]         nameservers:

`            `addresses: [8.8.8.8]

`        `routes:

\- to: default

`              `via: 192.168.10.1 version: 2

sudo netplan apply![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.010.png)

Done.

**Setting Up Splunk Enterprise (SE):**

1. Open a web browser and navigate to the Splunk website ([https://www.splunk.com](https://www.splunk.com/)).
1. Create an account or login to your account.
1. Under Products, click on “Free Trials & Downloads”.
4. Scroll down, under Splunk Enterprise click-on “Get My Free Trial”
4. Select the appropriate version of Splunk Enterprise for Linux (64-bit) and choose the Debian package (`.deb`) format.

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.011.jpeg)

sudo apt install ./splunk<version>.deb![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.012.png)

4. After the installation completes, start Splunk Enterprise by running: sudo /opt/splunk/bin/splunk start — accept-license![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.013.png)
4. Type ‘*y’* to agree with the license.
4. Splunk Enterprise will prompt you to create an administrator password. Follow the instructions to set a secure password.

**Step 4: Access Splunk Enterprise Web Interface**

1. Start up the Splunk web interface by running:

sudo /opt/splunk/bin/splunk start![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.014.png)

2. After loading, right click on the link beside “The Splunk web interface is at” and click-on ***Open Link***

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.015.jpeg)

You Can Access the Splunk GUI Based Web Interface on 192.168.10.10:8000

Use the Username and Password set during the installation to log into the administrator page. Setting up the Target Windows Machine : 

Check the IP Address of the Windows Machine 

ipconfig![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.016.png)

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.017.jpeg)

Fixing the IP address of the Windows Machine to easily forward the data using Splunk forwarder.

1. Go the Change Network Adapter

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.018.jpeg)

2. Select the Properties Section of the Eternet Adapter.

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.019.jpeg)

3. Go to Internet Protocol Version and set the IP address to static based on your need, in my case its 192.168.10.100

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.020.jpeg)

**Deploying the Splunk Universal Forwarder on Windows**

The [Splunk Universal Forwarder](https://www.splunk.com/en_us/download/universal-forwarder.html) is the best mechanism for collecting logs from servers and end-user systems. In order to collect logs at scale, it is necessary to deploy the Universal Forwarder to every system where log collection is required. Managing the deployment of the Universal Forwarder is best handled via whatever mechanism your organization uses to deploy software packages across machines in your organization. However, if you’re doing a one-off installation of the Universal Forwarder or don’t have a method of deploying MSIs, the installer may be an acceptable option. 

**Installation Steps**

**Obtain the Installation Package**

First, download the Splunk Universal Forwarder from Splunk’s [download page](https://www.splunk.com/en_us/download/universal-forwarder.html). You will need a [Splunk.com](https://www.splunk.com/en_us/download/universal-forwarder.html) account to access the download. In the event you need to download an older version of the Universal Forwarder, those packages are available on the [older releases](https://www.splunk.com/en_us/download/previous-releases/universalforwarder.html) page.

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.021.jpeg)

When running the installation wizard, you will be asked if you’re deploying the Universal Forwarder for an on- premise or Splunk Cloud deployment. If you have an environment managed by Hurricane Labs with a deployment server, you’ll always want to choose the on-premise option (even if you’re a Splunk Cloud customer), since all of the configurations will be managed by the deployment server.

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.022.png)

Set the IP Address to the Splunk Enterprices and the port to Default.

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.023.jpeg)

Complete the installation.

**Installing and Configuring Sysmon for Windows**

**What is Sysmon?**

Sysmon is part of the [Sysinternals suite](https://docs.microsoft.com/en-us/sysinternals/) and is useful for extending the default Windows logs with higher-level monitoring of events and process creations. Sysmon contains detailed information about process creations, networks connections, and file changes.

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.024.png)

**Sysmon Event ID’s**

- Event ID 1: Process creation
- Event ID 2: A process changed a file creation time
- Event ID 3: Network connection
- Event ID 4: Sysmon service state changed
- Event ID 5: Process terminated
- Event ID 6: Driver loaded
- Event ID 7: Image loaded
- Event ID 8: CreateRemoteThread
- Event ID 9: RawAccessRead
- Event ID 10: ProcessAccess
- Event ID 11: FileCreate
- Event ID 12: RegistryEvent (Object create and delete)
- Event ID 13: RegistryEvent (Value Set)
- Event ID 14: RegistryEvent (Key and Value Rename)
- Event ID 15: FileCreateStreamHash
- Event ID 16: ServiceConfigurationChange
- Event ID 17: PipeEvent (Pipe Created)
- Event ID 18: PipeEvent (Pipe Connected)
- Event ID 19: WmiEvent (WmiEventFilter activity detected)
- Event ID 20: WmiEvent (WmiEventConsumer activity detected)
- Event ID 21: WmiEvent (WmiEventConsumerToFilter activity detected)
- Event ID 22: DNSEvent (DNS query)
- Event ID 23: FileDelete (File Delete archived)
- Event ID 24: ClipboardChange (New content in the clipboard)
- Event ID 25: ProcessTampering (Process image change)
- Event ID 26: FileDeleteDetected (File Delete logged)
- Event ID 255: Error

![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.025.jpeg)

You can Download the Sysmon From the this Link : <https://download.sysinternals.com/files/Sysmon.zip>

[To Run the Sysmon under set of rule for Splunk we a using Sysmon Olaf Config : https://github.com/olafhartong/sysmon- modular/blob/master/sysmonconfig.xml ](https://github.com/olafhartong/sysmon-modular/blob/master/sysmonconfig.xml)

After Downloading both of the File, we will Install Sysmon using the olaf Config

.\Sysmon64.exe -i .\sysmonconfig.xml![](Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.026.png)

[ref1]: Aspose.Words.7cdf0365-dee7-48fb-88f5-90928c4b193c.003.png
