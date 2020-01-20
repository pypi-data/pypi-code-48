#!/usr/bin/python3
# Profile Settings

# from OnlySnarf.driver import Driver

class Profile:

    # profile settings are either:
    #   enabled or disabled
    #   display text, variable type, variable name in settings
    def __init__(self, data):
        # url path or file upload
        self.coverImage =  data.get("coverImage") or None
        # url path or file upload
        self.profilePhoto = data.get("profilePhoto") or None
        # text
        self.displayName = data.get("displayName") or ""
        # text in $
        # minimum $4.99 or free
        self.subscriptionPrice = data.get("subscriptionPrice") or "4.99"
        # text
        self.about = data.get("about") or ""
        # text
        self.location = data.get("location") or ""
        # text as url
        self.websiteURL = data.get("websiteURL") or None
        # text
        self.username = data.get("username") or ""
        # text, can't be changed
        self.email = data.get("email") or ""
        # text
        self.password = data.get("password") or ""
        # enabled or disabled
        self.emailNotifs = data.get("emailNotifs") or False
        # enabled or disabled
        self.emailNotifsNewReferral = data.get("emailNotifsNewReferral") or False
        # enabled or disabled
        self.emailNotifsNewStream = data.get("emailNotifsNewStream") or False
        # enabled or disabled
        self.emailNotifsNewSubscriber = data.get("emailNotifsNewSubscriber") or False
        # enabled or disabled
        self.emailNotifsNewTip = data.get("emailNotifsNewTip") or False
        # enabled or disabled
        self.emailNotifsRenewal = data.get("emailNotifsRenewal") or False
        # enabled or disabled
        self.emailNotifsNewLikes = data.get("emailNotifsNewLikes") or False
        # enabled or disabled
        self.emailNotifsNewPosts = data.get("emailNotifsNewPosts") or False
        # enabled or disabled
        self.emailNotifsNewPrivMessages = data.get("emailNotifsNewPrivMessages") or False
        # enabled or disabled
        self.siteNotifs = data.get("siteNotifs") or False
        # enabled or disabled
        self.siteNotifsNewComment = data.get("siteNotifsNewComment") or False
        # enabled or disabled
        self.siteNotifsNewFavorite = data.get("siteNotifsNewFavorite") or False
        # enabled or disabled
        self.siteNotifsDiscounts = data.get("siteNotifsDiscounts") or False
        # enabled or disabled
        self.siteNotifsNewSubscriber = data.get("siteNotifsNewSubscriber") or False
        # enabled or disabled
        self.siteNotifsNewTip = data.get("siteNotifsNewTip") or False
        # enabled or disabled
        self.toastNotifs = data.get("toastNotifs") or False
        # enabled or disabled
        self.toastNotifsNewComment = data.get("toastNotifsNewComment") or False
        # enabled or disabled
        self.toastNotifsNewFavorite = data.get("toastNotifsNewFavorite") or False
        # enabled or disabled
        self.toastNotifsNewSubscriber = data.get("toastNotifsNewSubscriber") or False
        # enabled or disabled
        self.toastNotifsNewTip = data.get("toastNotifsNewTip") or False
        # enabled or disabled
        self.fullyPrivate = data.get("fullyPrivate") or False
        # enabled or disabled
        self.enableComments = data.get("enableComments") or False
        # enabled or disabled
        self.showFansCount = data.get("showFansCount") or False
        # enabled or disabled
        self.showPostsTip = data.get("showPostsTip") or False
        # enabled or disabled
        self.publicFriendsList = data.get("publicFriendsList") or False
        # selection of countries
        self.ipCountry = data.get("ipCountry") or Profile.get_country_list()
        # text of ip ranges
        self.ipIP = data.get("ipIP") or ""
        # enabled or disabled
        self.watermark = data.get("watermark") or True
        # enabled or disabled
        self.watermarkPhoto = data.get("watermarkPhoto") or False
        # enabled or disabled
        self.watermarkVideo = data.get("watermarkVideo") or False
        # the custom watermark text
        self.watermarkText = data.get("watermarkText") or ""
        if self.username and str(self.username) != "" and self.watermarkText == "":
            self.watermarkText = "OnlyFans.com/{}".format(self.username)
        # the obs live server
        self.liveServer = data.get("liveServer") or ""
        # the obs live server key
        self.liveServerKey = data.get("liveServerKey") or ""

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        return setattr(self, key, val)

    def syncFrom(self):
        # opens every settings page in the browser from pages or all
        # gets necessary variables from browser
        variables = Profile.get_setting_variables()
        pages = []
        for var in variables:
            if var[1] not in pages:
                pages.append(var[1])
        for page in pages:
            pass
            # Driver.go_to_settings_page(page)
        pass            

    def syncTo(self):
        # opens every settings page in the browser from pages or all
        # updates necessary variables in browser
        pass

    @staticmethod
    def get_country_list():
        return ["USA","Canada"]

    @staticmethod
    def get_pages():
        return ["profile", "advanced", "messaging", "notifications", "security", "story", "other"]

    @staticmethod
    def get_variables_for_page(page):
        variables = get_settings_variables()
        vars_ = []
        for var in variables:
            if str(var[1]) == str(page):
                vars_.append(var)
        return vars_

    @staticmethod
    def get_setting_variable(key):
        variables = get_setting_variables()
        for var in variables:
            if str(var[0]) == str(key):
                return var
        return None

    def update_value(self, key, value):
        try:
            if key == None or str(key) == "" or str(key) == "None": return
            self[key] = value
        except Exception as e:
            print(e)

    # returns list of settings and their classes
    # ["settingVariableName","pageProfile","inputType-text"]
    
def get_settings_variables():
    return [

        ### Profile ###

        ["coverImage","profile","file"],
        ["profilePhoto","profile","file"],
        ["username","profile","text"],
        ["displayName","profile","text"],
        ["subscriptionPrice","profile","text"],
        ["referralReward","dropdown"],
        ["about","profile","text"],
        ["location","profile","text"],
        ["websiteURL","profile","text"],

        #### Account / Advanced ###

        # id="input-email"
        ["email","advanced","text"],
        # id="old_password_input"
        ["password","advanced","text"],
        # id="new_password_input"
        ["newPassword","advanced","text"],
        # id="new_password2_input"
        ["confirmPassword","advanced","checkbox"],

        ### Chats / Messages ###
        # welcome message toggle
        # welcome message text
        # welcome message file
        # welcome message record voice, video
        # welcome message price
        # welcome message submit

        # hide outgoing message toggle
        # show full text of message in the notification email

        ### Notifications ###

        # id="push-notifications"
        ["emailNotifs","notifications","toggle"],
        # id="email-notifications"
        ["emailNotifsReferral","notifications","checkbox"],
        ["emailNotifsStream","notifications","toggle"],
        ["emailNotifsSubscriber","notifications","toggle"],
        ["emailNotifsTip","notifications","toggle"],
        ["emailNotifsRenewal","notifications","toggle"],
        # this is a dropdown
        ["emailNotifsLikes","notifications","dropdown"],
        ["emailNotifsPosts","notifications","toggle"],
        ["emailNotifsPrivMessages","notifications","toggle"],
        ["siteNotifs","notifications","toggle"],
        ["siteNotifsComment","notifications","toggle"],
        ["siteNotifsFavorite","notifications","toggle"],
        ["siteNotifsDiscounts","notifications","toggle"],
        ["siteNotifsSubscriber","notifications","toggle"],
        ["siteNotifsTip","notifications","toggle"],
        ["toastNotifsComment","notifications","toggle"],
        ["toastNotifsFavorite","notifications","toggle"],
        ["toastNotifsSubscriber","notifications","toggle"],
        ["toastNotifsTip","notifications","toggle"],

        ### Security ###

        ["fullyPrivate","security","checkbox"],
        ["enableComments","security","toggle"],
        ["showFansCount","security","toggle"],
        ["showPostsTip","security","toggle"],
        ["publicFriendsList","security","toggle"],
        ["ipCountry","security","list"],
        # id="input-blocked-ips"
        ["ipIP","security","list"],
        # id="hasWatermarkPhoto"
        ["watermarkPhoto","security","toggle"],
        # id="hasWatermarkVideo"
        ["watermarkVideo","security","toggle"],
        # placeholder="Watermark custom text"
        ["watermarkText","security","text"],

        ### Story ###
        # allow message replies - nobody
        # allow message replies - subscribers

        ### Other ###

        ["liveServer","other","text"],
        ["liveServerKey","other","text"],
        ["welcomeMessageToggle","other","toggle"],
        ["welcomeMessageText","other","text"],

    ]

