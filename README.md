# Web project for analyzing social network
This project was realized on Python with Flask library. It allows you to create a PDF file with some statistics about particular vk page (but this page should not be closed).<br>

## Link: [service](http://45.67.35.81:5555/vk_statistics)

### Tutorial:
1. Install docker and docker-compose
2. Clone this repository

  * ```console
    user@user:~$ git clone https://github.com/CI314X/social-network-analyzer.git
    ```
    
3. Fill a config file:

  * MAIL_USERNAME: name of your mail box without domen.
  * MAIL_PASSWORD: password of this mail box.
  * SECRET_KEY and WTF_CSRF_SECRET_KEY: some random strings.
  * ADMINS: your full name of mail box.
  * access_token: tokens for vk class (https://vkhost.github.io/). It is recommended to specify more than 2 tokens.
  * logger_filename: the pathname of the source file where the logging call was made.
  * telegram_token (optional): token for telegram bot. You have to create bot in telegram via BotFather and copy an authentication token (https://core.telegram.org/bots)

4. Build docker:

*  ```console
   user@user:~$ docker-compose up --build
   ```

<!-- #### Local link: http://localhost:5555/ -->

### Front page
<p align="left">
  <img src="static/readme_picture_vk_stat.png" width="800" title="screenshot">
</p>

### Instruction for running project on Amazon AWS:

* Create an account in a service
* Create public and private keys: my_key.pem
* After config your virtual machine, run next:
```console
user@user:~$ chmod 400 my_key.pem
user@user:~$ sudo ssh -i my_key.pem ec2-user@ec2-3-137-176-123.us-east-2.compute.amazonaws.com
user@user:~$ sudo yam install -y docker git
user@user:~$ docker-compose up --build
```
