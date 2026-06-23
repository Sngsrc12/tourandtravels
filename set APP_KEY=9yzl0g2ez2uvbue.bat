set APP_KEY=9yzl0g2ez2uvbue
set REDIRECT_URI=http://localhost
set STATE=12345
echo "https://www.dropbox.com/oauth2/authorize?client_id=%APP_KEY%&response_type=code&token_access_type=offline&redirect_uri=%REDIRECT_URI%&state=%STATE%"

https://www.dropbox.com/oauth2/authorize?client_id=9yzl0g2ez2uvbue&response_type=code&token_access_type=offline&redirect_uri=&state=12345

https://www.dropbox.com/oauth2/authorize?client_id=9yzl0g2ez2uvbue&response_type=code&token_access_type=offline&redirect_uri=http://localhost&state=12345

http://localhost/?code=aX5X_Xx2F38AAAAAAAAEO4GaW2ap9maOqeqLywa6Xig&state=12345


http://localhost/?code=aX5X_Xx2F38AAAAAAAAEPrzuKcpiHryt6tFcM5LBQ5w&state=12345


set AUTHORIZATION_CODE=aX5X_Xx2F38AAAAAAAAEPrzuKcpiHryt6tFcM5LBQ5w
set APP_SECRET=2vmc871245bt8z5
curl -X POST https://api.dropbox.com/oauth2/token ^
-d code=%AUTHORIZATION_CODE% ^
-d grant_type=authorization_code ^
-d client_id=%APP_KEY% ^
-d client_secret=%APP_SECRET% ^
-d redirect_uri=%REDIRECT_URI%



https://www.dropbox.com/oauth2/authorize?client_id=i6njerp0zlda35l&response_type=code&token_access_type=offline


set AUTHORIZATION_CODE=BvnkFR3KOqAAAAAAAAAA5aPq-6vg3HW-bmTyg4SMPiA
set APP_SECRET=yonvxndkvdmkhdi
curl -X POST https://api.dropbox.com/oauth2/token ^
-d code=%AUTHORIZATION_CODE% ^
-d grant_type=authorization_code ^
-d client_id=%APP_KEY% ^
-d client_secret=%APP_SECRET% ^
-d redirect_uri=%REDIRECT_URI%