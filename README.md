# releasenotesgen

### Install openai and requests libraries
``` bash
pip3 install requests openai
```

### Download from source
``` bash
cd /Users/<user>/repos
git clone https://github.com/celery-payroll/releasenotesgen.git
cd releasenotesgen
```

### Make symlink so you can run it from everywhere
``` bash
ln -s releasenotesgen /usr/local/bin/releasenotesgen
```

### Copy template configfile to your project
``` bash
cp releasenotesgen.yml /Users/<user>/repos/myProject
```
### Usage
change releasenotesgen.yml to your needs
and run 
``` bash
releasenotesgen
```
