# Current ticket (regarding an online multi-players Blackjack mobile game)
• Figuring out a C++ executable to delete all instances in AWS Lambda;\
• Sub-path coming up;

# Sub-goal
1. Suppose there are some players in Blackjack. For example, let's say we are having three players in a play room. We consider the current point of a play a component in a vector, v.\
Thus, dim(v) == 3. Between the DB, which is either DynamoDB/MySQL, and a player side (written in C# based on Unity), we just need to update the component accordingly every time. For example given (1\/* ,2,3)\
when Aces are every point as the player desires; then, it could be changed to (1\/* ,4,3). Using vectors like that is better cuz the app is more scalable when we are applying AI structure to it. Most likely data tuning from\
Scikit-learn and neural networks in TensorFlow. Depends on the dimensions, we might need to use Word2Vec during the process of embedding.     

# Intro
aws_linux_walkk
# Github repo set-up tutorial
If you would like to quickly learn how to set up a Github repository, this is the tutorial I made for my sophomores\
in my CSC322 group project as their team lead during my last term at UVic:\
https://youtu.be/KYdwu_zLXec?si=KNOLvxa3vbwfyRhZ

# EC2 instance set up 
(Under construction)

# Docker escalates compiling
(Under construction)

# Lambda ( C++ && python )
(Under construction)

# Usage of searchRPM script
`sudo chmod +x ./searchRPM`\
`sudo ./searchRPM <targetted-column> <desired-substring>`\
For example, if I wanna search everything containing "mysql":\
`sudo ./searchRPM 0 mysql`

If it has that, the whole name of the rpm package will be printed out, besideds the total # of searching.

# VPC config (Notebook_EC2_RDS.ipynb)
It teaches you how to set up a jump box EC2, subnets, VPCs, route tables, MySQL database. Then use a JupyterNotebook to play with it:\
https://youtu.be/cWzT9-Q76Es

## Important point-outs:
• For installing Openssl11 (manually):\
`wget https://mirror.stream.centos.org/9-stream/AppStream/x86_64/os/Packages/compat-openssl11-1.1.1k-3.el9.x86_64.rpm`\
`sudo yum localinstall compat-openssl11-1.1.1k-3.el9.x86_64.rpm`\
• Redhat MySQL repo:\

https://dev.mysql.com/get/mysql84-community-release-el9-1.noarch.rpm
## Outcomes
**• JupyterNotebook fetch-ups:**

![notebook-fetchup!](https://s3-walkk.s3.us-east-1.amazonaws.com/notebook_out.PNG)
\
Link:\
https://s3-walkk.s3.us-east-1.amazonaws.com/notebook_out.PNG

**• MySQL fetch-ups:**
\
\
![linux_out!](https://s3-walkk.s3.us-east-1.amazonaws.com/linux_out.PNG)
\
Link:\
https://s3-walkk.s3.us-east-1.amazonaws.com/linux_out.PNG
\
\
**Note: Images powered by AWS S3 Bucket.**
