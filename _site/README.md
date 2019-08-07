Markup, style data and media for the yoshimi website,
along with a simple site generation script.

Python 2.7+ is required to generate the site.

Run `./gen_site` to generate the site.
The resulting files will be placed in a directory called 'out'

If you want to write the output somewhere else, you can use the `BUILD_DIR`
environment variable, for example like this:
```
BUILD_DIR=/home/me/www/my_audio_websites/yoshimi/ ./gen_site
```
or
```
export BUILD_DIR=/home/me/www/my_audio_websites/yoshimi/
./gen_site
```

