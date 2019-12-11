OKAPI="${OKAPI:-https://okapi-fse-eu-central-1.folio.ebsco.com}"
FILE=$1


TOKEN=$( curl -s -S -D - -H "X-Okapi-Tenant: diku" -H "Content-type: application/json" -H "Accept: application/json" -d '{"tenant":"fs00001000","username":"admin","password":"4ChalmersU0T"}' $OKAPI/authn/login | grep -i "^x-okapi-token: " )

curl -s -S -D - -H "$TOKEN" -H "X-Okapi-Tenant: diku" -H "Content-type: application/json" -H "Accept: text/plain" $OKAPI/inventory/items?query=(status.name=="Missing")