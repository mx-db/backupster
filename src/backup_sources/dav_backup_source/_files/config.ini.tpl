[general]
status_path = "$VDIR_PATH/status/"

#### Contacts ####

[pair contacts_i]
a = "contacts_local_i"
b = "contacts_remote"
collections = ["from b"]
conflict_resolution = "b wins"

[pair contacts_c]
a = "contacts_local_c"
b = "contacts_remote"
collections = ["from b"]
conflict_resolution = "b wins"

[storage contacts_local_i]
type = "filesystem"
path = "$BAK_PATH/contacts/contacts_i/"
fileext = ".vcf"

[storage contacts_local_c]
type = "singlefile"
path = "$BAK_PATH/contacts/contacts_c/%s.vcf"

[storage contacts_remote]
type = "carddav"
url = "$CARDDAV_URL"
username = "$CARDDAV_USERNAME"
password = "$CARDDAV_PASSWORD"


#### Calendar ####

[pair calendar_i]
a = "calendar_local_i"
b = "calendar_remote"
collections = ["from b"]
conflict_resolution = "b wins"
metadata = ["color", "displayname", "description", "order"]

[pair calendar_c]
a = "calendar_local_c"
b = "calendar_remote"
collections = ["from b"]
conflict_resolution = "b wins"
metadata = ["color", "displayname", "description", "order"]

[storage calendar_local_i]
type = "filesystem"
path = "$BAK_PATH/calendar/calendar_i/"
fileext = ".ics"

[storage calendar_local_c]
type = "singlefile"
path = "$BAK_PATH/calendar/calendar_c/%s.ics"

[storage calendar_remote]
type = "caldav"
auth = "basic"
url = "$CALDAV_URL"
username = "$CALDAV_USERNAME"
password = "$CALDAV_PASSWORD"