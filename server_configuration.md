# Configuring server side

### Running streamlit app as an service

The [streamlit_equity.service](streamlit_equity.service) -file should be copied to:

`/etc/systemd/system/streamlit_equity.service`

### Configuring Nginx

The contents of [nginx.conf](nginx.conf) -file should be copied into following file:

`/etc/nginx/sites-available/streamlit_equity`

After this, a symbolic link to this file needs to be added as follows:

`sudo ln -s /etc/nginx/sites-available/streamlit_equity /etc/nginx/sites-enabled/`

### Certbot (SSL configuration)

Install necessary packages:

`sudo apt install certbot python3-certbot-nginx`

Get SSL certificates (certbot renews them automatically):

`sudo certbot --nginx -d equity.gistlab.science -d www.equity.gistlab.science`

