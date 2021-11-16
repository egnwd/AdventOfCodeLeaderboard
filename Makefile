.PHONY: package deploy

package:
	pip3 install --target ./package -r ./requirements.txt
	cd package
	zip -r ../package.zip .
	cd ..
	zip -g package.zip leaderboard.py

deploy: package
	serverless deploy --stage prod