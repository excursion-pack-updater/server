# Excursion Pack Updater &mdash; Server
## Requirements
* Python 3
* Libraries listed in [`requirements.txt`](requirements.txt)
* Outgoing email server (for login flow)

## Howto
With the possible exception of [Creating a Modpack](#creating-a-modpack), most of this should be familiar if you've ever used Django and its admin site before.

### Installation
* Make a folder to house the Django project (henceforth referred to as `$root`) and clone this repo into a subfolder
	```bash
	mkdir $root
	git clone https://github.com/excursion-pack-updater/server.git $root/epu/
	```
* (optional) Set up an isolated Python environment, e.g. with `venv`:
	```bash
	python -m venv $root/.venv
	source $root/.venv/bin/activate
	```
* Install dependencies and create the Django project
	```bash
	pip install -r $root/epu/requirements.txt
	python -m django startproject django_env $root
	```
* Configure `$root/django_env/settings.py`:
	* Set `DEBUG = False` (helpful to defer this until your app server and reverse proxy are configured correctly)
	* Add your (sub)domain to `ALLOWED_HOSTS`
	* Append `"epu"` to `INSTALLED_APPS`
	* (optional) Configure `DATABASES` to use something beyond the default of SQLite. See [Django documentation](https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-DATABASES) for details
	* (if needed) Configure [email settings](https://docs.djangoproject.com/en/4.1/topics/email/#smtp-backend)
	* Configure `STATIC_URL`/`STATIC_ROOT` & `MEDIA_URL`/`MEDIA_ROOT`. `*_ROOT` denote directories, which should be servable by your reverse proxy
		```bash
		STATIC_URL = "static/" # this should already exist
		STATIC_ROOT = str(BASE_DIR / "static") # collects static assets (CSS, JS) into $root/static
		
		MEDIA_URL = "media/" # for dynamic content, in EPU's case instance zips and client binaries
		MEDIA_ROOT = str(BASE_DIR / "media")
		```
	* (optional) Clear all entries in `AUTH_PASSWORD_VALIDATORS`. This will make it easier to use throwaway passwords in subsequent steps
* Configure `$root/django_env/urls.py`:
	* If mounting at the root of a (sub)domain
		```python
		# ...
		from django.urls import include, path # change
		
		urlpatterns = [
			# ...
			path("", include("epu.urls", namespace="epu")), # add
		]
		```
	* If mounting under some subpath, e.g. `https://my.tld/epu/`. This path must also be hardcoded into `STATIC_URL`/`MEDIA_URL`
		```python
		# ...
		from django.urls import include, path # change
		
		# fixes the `View Site` link in admin
		# must have leading slash unlike patterns -- used verbatim as link target
		admin.site.site_url = "/epu/" # add
		
		urlpatterns = [
			path("epu/admin/", admin.site.urls) # change
			path("epu/", include("epu.urls", namespace="epu")), # add
		]
		```
* Run database migrations, collect static files, and create an administrator account:
	```bash
	$root/manage.py migrate
	$root/manage.py collectstatic
	$root/manage.py createsuperuser # password can be garbage
	```
* (optional) Run through [Django's deployment checklist](https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/)
* Set up and launch your *SGI server and reverse proxy, e.g. with [uwsgi](https://uwsgi-docs.readthedocs.io/en/latest/) and Nginx:
	* `uwsgi.ini` (and started with `uwsgi --ini uwsgi.ini`):
		```ini
		[uwsgi]
		vacuum = true
		plugins = python
		need-app = true
		chdir = $root # still referring to the folder originally created at step 1
		module = django_env.wsgi:application
		socket = $root/uwsgi.sock
		chmod-socket = 757
		home = $root/.venv # if you created a venv/virtualenv/etc
		```
	* `nginx.conf`:
		```nginx
		server {
			listen 443 ssl http2;
			server_name epu.mysite.tld;
			
			location / {
				client_max_body_size 64m;
				uwsgi_pass unix:///$root/uwsgi.sock;
				include uwsgi_params;
			}
			
			location /static {
				alias $root/static/;
			}
			
			location /media {
				alias $root/media/;
			}
		}
		```
	* For other deployment options, consult the [Django documentation](https://docs.djangoproject.com/en/4.1/howto/deployment/)
* EPU should now be up and running! Log in with the account you created earlier. Once logged in, visit the now-visible `admin` link in the top right
* Create client binaries (click `Add` next to `Client Binaries`.) Download each platform's zip from [the client repo](https://github.com/excursion-pack-updater/client/releases), and upload them to this form. Fill out the corresponding version in the description field. Click `Save`
* Done! Now you may move on to creating packs

### Creating a Modpack
* Create a git repository containing the modpack's `mods/`, `config/`, and any other required files/directories (e.g. `kubejs/`.) If needed, push the repository somewhere visible to your EPU backend (e.g. a [gitea](https://gitea.io) instance)
	* This repository may be shared with an active game server, in which case you should use the [recommended gitignore](modpack.gitignore)
* Open MultiMC and create a new instance, taking care to select the correct version of Minecraft. This instance will be temporary; the name does not matter
* Right click the instance, select `Edit Instance`, and from the `Version` tab install the required mod platform (Forge/Fabric) of appropriate version
* Close the settings window. Right click the instance again, and this time select `Instance Folder`. Create a zip containing at least `mmc-pack.json`. `instance.cfg` may be skipped as EPU will generate it on the fly (due to platform specifics.) Save the zip somewhere, and delete the instance
	* If you so desire, you may also include in this zip other things such as a pre-filled `server.dat`, a default `options.txt` (keybinds/video settings/etc,) or anything else that should be excluded from updates
* Log in to your EPU backend, visit the admin interface, and add a new pack (from homepage, click the `Add` button next to `Packs`)
* Fill out pack details such as the name and icon, select client binaries created during installation, and most importantly set the git repository URL
	* Dulwich (the library EPU uses to interface with git) supports SSH, HTTP, and local filesystem paths; and so these all should work for the repo URL as well. If you need to use an SSH key, (at present) it will have to be in the usual location (`$HOME/.ssh/id_rsa`) and must not be password protected
* Upload the previously created instance zip, and save
* Return to EPU's homepage. Click the `repo status` link. Click the `Refresh repositories` link. Verify EPU was able to query the repository without issue
* Done, go distribute your new pack!

### User Management
If you don't need the power to revoke access to pack updates on an individual basis, then you can skip making accounts for your users. However it is still recommended to at least make a dummy account to download generated pack zips; administrators' API keys can be used for more than downloading pack files

To make users:
* Log in to your EPU backend's admin interface and add a new user by clicking `Add` next to `Users`
* Fill out username. Passwords are unused, but unfortunately cannot be (reasonably) disabled, and so you will need to fill in a garbage password
* Press the `Save` button. The page will refresh, but more fields will be available now. Fill in the user's email, this is required to log in. Press `Save` once again
* Done! The user may now log in with their email, and download packs

If you decide to revoke an individual's access, you may simply uncheck the `Active` field. This will disable their ability to log in and download new packs, as well as forbid them updates to existing packs.

If you wish to create new adminstrator accounts, in addition to rerunning `manage.py createsuperuser` you may instead create an account as outlined above and simply check the `Superuser status` field.
