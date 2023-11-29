push: 
	git add . 
	- git commit -m $(commit-name)
	git push

update:
	git add . 
	- git commit -m "update"
	git push

upgrade: 
	git pull 
	python3 main.py