## Run:
```console
user@user:~$ docker-compose up --build
user@user:~$ docker exec -it analyzer_social_media_flask_1 bash
```

### Link:
http://localhost:5555/vk_statistics

## Amazon AWS
```console
user@user:~$ chmod 400 key.pem
user@user:~$ sudo ssh -i key.pem ec2-user@ec2-3-137-176-123.us-east-2.compute.amazonaws.com
user@user:~$ sudo yam install -y docker git
user@user:~$ docker-compose up --build
```

### Link:
http://ec2-3-137-176-123.us-east-2.compute.amazonaws.com:5555/vk_statistics