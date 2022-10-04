# InstaMonitor
InstaMonitor is a tool that allows you to monitor your Instagram followers. <br/>
You can see if some peoples have unfollowed your account, or if they force you to unfollow theirs. <br/>
On each execution, the script save the results in the local file, to allow you to keep each dates for each new actions.

## 💡 Prerequisite
- [Python 3](https://www.python.org/downloads/release/python-370/)
- [Instagram account](https://www.instagram.com/) for log in to this app
- [Instagram account](https://www.instagram.com/) to target (can be the same one used for the connection)

## 🛠️ Installation
### With Github

```bash
git clone https://github.com/shader69/instamonitor.git
cd instamonitor/
python setup.py install
```

## 📚 Usage:
### Run the app in Python console
```python
from instamonitor.core import main

# Set variables
targeted_username = 'username'
connected_user_session_id = None

# Execute main function
main(targeted_username, connected_user_session_id)
```
### Or in terminal
```bash
instamonitor -s [sessionid]
```
```bash
python instamonitor/demo.py
```

## 📈 Example of result

| Username                                      | I follow him   | He follow me   | Last check date |
|-----------------------------------------------|----------------|----------------|----------------|
| j.doe                                         | True           | True           |                |
| <span style="color:red">shelly_munoz</span>   | True           | False          | 2022-08-24     |
| <span style="color:yellow">dennismoore</span> | False          | True           |                |
| brown__j                                      | False          | False          | TODAY          |
| tracywalton31                                 | True           | False          |                |


#### Color code:
* <span style="color:red">**RED**</span> : you follow this user, but he doesn't follow you
* <span style="color:yellow">**YELLOW**</span> : this user follow you, but you don't follow him


## 📚 To retrieve the instagram sessionID
![](https://files.catbox.moe/1rfi6j.png)

## Thank you to :
- [megadose](https://github.com/megadose)