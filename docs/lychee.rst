
Lychee configuration
--------------------

1. Install PHP support

   ::

        $ sudo apt-get install php7.0-fpm php7.0-gd libgd2-xpm-dev libpcrecpp0v5 libxpm4
2. Install Nginx

   ::

        $ sudo apt-get install nginx
3. Update permissions on the directory /var/www to Apache group (www-data)

   ::

        $ sudo chown -R www-data:www-data /var/www
4. Install MySQL and PHP support

   ::

        $ sudo apt-get install -y php7.0-mysql mysql-server
5. Edit the /etc/php/7.0/fpm/php.ini file by adding at the end :

   ::

        extension = php_mbstring.dll
        extension = php_exif.dll
        extension = php_gd2.dll
        max_execution_time = 200
        post_max_size = 200M
        upload_max_size = 200M
        upload_max_filesize = 20M
        max_file_uploads = 100
6. Restart the PHP service

   ::

        $ service php7.0-fpm restart
7. Retrieve the latest version of Lychee

   ::

        $ cd /var/www
        $ sudo git clone https://github.com/electerious/lychee.git
        $ sudo chown -R www-data:www-data /var/www
8. Remove default Nginx configuration

   ::

        $ sudo rm /etc/nginx/sites-available/default
9. And then create the file ``/etc/nginx/sites-available/lychee`` with the following content

   ::

       server {
          root /var/www/lychee;
          index index.php index.html index.htm;
          location ~ .php$ {
             fastcgi_pass unix:/var/run/php/php7.0-fpm.sock;
             fastcgi_index php/index.php;
             include fastcgi.conf;
          }
       }
10. Enable the site

   ::

        $ sudo ln -s /etc/nginx/sites-available/lychee /etc/nginx/sites-enabled/lychee
11. Open the file ``/etc/nginx/nginx.conf`` and add/modify the following line inside http {…}

   ::

        client_max_body_size 20M;
13. Reload the nginx service

   ::

        $ service nginx reload
14. Create a MySQL user database creation

   ::

     $ sudo mysql -u root -p  # Type [ENTER] when asking for password
     MariaDB [(none)]> CREATE USER 'lychee'@'localhost' IDENTIFIED BY 'mypassword';
     MariaDB [(none)]> GRANT ALL PRIVILEGES ON * . * TO 'lychee'@'localhost';
     MariaDB [(none)]> FLUSH PRIVILEGES;
     MariaDB [(none)]> quit
15. Appointment now with browser at your Raspberry
16. Install folder synchro from `https://github.com/GustavePate/lycheesync`_
