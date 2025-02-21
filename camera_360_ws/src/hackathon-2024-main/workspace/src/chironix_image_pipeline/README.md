# chironix_image_pipeline

## isaac_ros_image_proc

### Nvidia VPI
We are using the rectify from isaac ros this will need nvidia VPI, this is already installed on Jetson.
Note that cuda tookit should be already installed and compatible with the driver.

On developer x86_64 machine:

```bash
sudo apt install software-properties-common gnupg
sudo apt-key adv --fetch-key https://repo.download.nvidia.com/jetson/jetson-ota-public.asc
sudo add-apt-repository 'deb http://repo.download.nvidia.com/jetson/x86_64/focal r35.4 main'
sudo apt update
sudo apt install libnvvpi2 vpi2-dev vpi2-samples

```

if python binding is needed: `sudo apt install python3.8-vpi2`
