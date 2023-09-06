push: 
	git add . 
	- git commit -m $(commit-name)
	git push

update:
	git add . 
	- git commit -m "update"
	git push