# Mini Inference Daemon

## Created/identified the project folder on your Mac
~/Desktop/miniinfer
Tried Multipass for the Linux VM
multipass launch 24.04. It failed because of the QEMU image-conversion error.

## Checked your Mac architecture
uname -m -> arm64

## Checked available disk space
df -h /

## Switched from Multipass to Lima becoz qema-img was causing crash
limactl version -> Lima 2.2.0

## Created the Linux VM
limactl start --name=miniinfer-vm --cpus 2 --memory 3 --disk 15 template://ubuntu-lts

Your VM has:
2 CPUs
3 GiB RAM
15 GiB disk
ARM64
VZ virtualization

## Started/entered the VM
limactl shell miniinfer-vm -> you enter into the home directory (/Users/anushka)

## Verified the Mac files are visible inside the VM
pwd
ls

## Navigated to your actual project
cd /Users/anushka/Desktop/miniinfer
You're currently here: /Users/anushka/Desktop/miniinfer

## Commands
cat /etc/os-release -> a standard Linux file containing information about the operating system.
systemctl --version -> systemctl is the command we use to interact with systemd, Linux's service manager.
stat -fc %T /sys/fs/cgroup -> Does this Linux environment have cgroup available for the resource-limit experiments we're going to do later?
cgroup = control group for putting processes into a group and controlling/monitoring their resource usage.
Linux
│
├── normal processes
│
└── miniinfer service
       │
       ├── worker 1
       ├── worker 2
       └── worker 3
       
       cgroup controls this group
       ├── How much CPU can it use?
       ├── How much memory can it use?
       └── How much has it actually used?

Your miniinfer.service will eventually contain:
MemoryMax=1G
CPUQuota=400%

Meaning roughly:
MemoryMax=1G → the service's cgroup cannot use more than 1 GiB of memory
CPUQuota=400% → it can use up to 4 CPU cores' worth of CPU time (assuming the system has that capacity)

So if your daemon starts consuming too much memory:

Mini Inference Daemon
        ↓
uses memory
        ↓
cgroup monitors/limits it
        ↓
MemoryMax reached
        ↓
Linux can take action

## Create the folders
mkdir -p daemon client systemd experiments 
daemon/ → the actual Mini Inference Daemon code
client/ → program that sends requests to the daemon
systemd/ → the .service file that makes Linux run the daemon as a service
experiments/ → scripts/results for the resource-limit, shutdown, overload, FD-leak, strace, etc. experiments

g