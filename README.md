# OpenCTI x QRadar

### Version history :

+ 1.0 : Coming soon :calendar:

---

### Introduction :

OpenCTI x QRadar is a program which provide a way to interconnect OpenCTI and QRadar.
For those who don't know OpenCTI, it is a cyber threat intelligence (CTI) platform and QRadar is the SIEM solution of IBM.

---

### Purpose of the project :

OpenCTI x QRadar project aims to populate QRadar referentials with OpenCTI datas which are cyber threats. The first version will only focus on IPv4 threat.

---

### Prerequisites :

+ OpenCTI account (it's free, just go on the link in sources and register) or you can setup your own OpenCTI server, it's up to you :smile:
  + Get your API token throught the profile page on OpenCTI platform then the value under "API access" box
+ QRadar instance, you can use QRadar Community Edition, it's quite easy to setup and it's also free (I wrote an article about the installation, you will find the link in sources)
  + Get "Authorized services" token with "Admin" permission
  + Create a reference map in order to store malicious artefacts
+ Machine with Python3 where you can execute the code

---

### Program description

This program have 4 main functions :

1. function to get information of a QRadar referential
2. function to get OpenCTI observables
3. function to upload datas in a QRadar referential
4. function to clean datas which are not accurate

You will find more details in this schema :

![openctixqradar_functions](https://github.com/staze0/openctiXqradar/blob/819ca49e6cf84d4556c5f2dff1384b38d895c8c6/openctixqradar_functions.png)

Finally, all the function are commented with much more details.

---

### Examples :

*Coming soon :calendar:*

---

### Sources :

+ [OpenCTI GitHub page](https://github.com/OpenCTI-Platform/opencti)
+ [QRadar Community Edition main page](https://www.ibm.com/community/qradar/ce/)
+ [QRadar CE installation & first configuration](https://staze.fr/comment-surveiller-vos-equipements-partie-1/)
