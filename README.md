<img src="https://github.com/Roestlab/massseer/assets/32938975/0def9673-d1ec-43ba-97dc-10208c8911de" alt="MassSeer_Logo_Full_Small" width="500" />

MassSeer is a powerful platform designed for researchers and analysts in the field of mass spectrometry. It enables the visualization of chromatograms (spectra and ion mobiliograms to come...) and provides a flexible environment for rapid algorithm testing and parameter optimization, crucial for data analysis and experimental design. This tool is an indispensable asset for researchers and laboratories working with DIA (Data-Independent Acquisition) data.

Key Features:

- **Chromatogram Visualization**: View and analyze chromatograms with ease, allowing for in-depth examination of mass spectrometry data.

- **Algorithm Testing**: Experiment with various data analysis algorithms and workflows, facilitating the development and fine-tuning of custom algorithms.

- **Parameter Optimization**: Optimize parameters for data analysis tools like OpenSwathWorkflow, ensuring the best results for your specific experiments.

- **User-Friendly Interface**: A user-friendly and intuitive interface makes it accessible to both beginners and experts in the field.

- **Data Exploration**: Dive into your mass spectrometry data, investigate peaks, and gain insights to make informed decisions.

- **Customization**: Adapt the tool to your specific research needs, allowing for tailored analysis and results.

- **Rapid Prototyping**: Quickly prototype and test ideas, saving time and resources in the development of mass spectrometry workflows.

- **Data Integration**: Seamlessly import, process, and export data, facilitating data sharing and collaboration.

This tool empowers researchers to take control of their mass spectrometry data, experiment with algorithms, and optimize parameters to enhance the accuracy and efficiency of their research. It's a valuable resource for laboratories and researchers working in the field of mass spectrometry, streamlining their workflows and contributing to scientific advancements.

![image](https://github.com/Roestlab/massseer/assets/32938975/215db9e9-0322-4cd4-8472-ad7897290daa)

# Installing MassSeer

## Installing from cloned directory

Run git clone

```
git clone https://github.com/Roestlab/massseer.git
```

Change into massseer directory

```
cd massseer
```

Pip install using *setup.py*

```
pip install -e .
```

## Installing from PyPi (...Still to Come)

```
pip install MassSeer
```

## Installing dependencies

```
pip install -r requirements.txt
```

# Running MassSeer GUI

```
MassSeer gui
```

# Running MassSeer GUI from a Remote Machine

Login to your remote machine

```
your_user_name@remote_ip_address
```

Navigate to MassSeer directory and start GUI. 

'''

your_user_name@remote_ip_address
'''

You will receive a message letting you know you can view Streamlit app in your browser with two URLs. 

'''

  Network URL: http://192.168.142.176:8501
  External URL: http://142.150.84.40:8501
'''

In your local machine, start a fresh terminal window. And enter the following command. Replace 'XXXX' with the last 4 digits from the URLs above

'''

ssh -NfL localhost:XXXX:localhost:XXXX your_user_name@remote_ip_address
'''

Now you can copy Network/External url to your local machine browser and use MassSeer. 
