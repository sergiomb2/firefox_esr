pref("app.update.auto",                     false);
pref("app.update.enabled",                  false);
pref("app.update.autoInstallEnabled",       false);
pref("browser.backspace_action",            2);
pref("browser.display.use_system_colors",   true);
pref("browser.download.folderList",         1);
pref("browser.link.open_external",          3);
pref("browser.shell.checkDefaultBrowser",   false);
pref("general.smoothScroll",                true);
pref("general.useragent.vendor",            "Red Hat");
pref("general.useragent.vendorSub",         "FIREFOX_RPM_VR");
pref("intl.locale.matchOS",                 true);
pref("storage.nfs_filesystem",              false);
pref("dom.ipc.plugins.enabled.nswrapper*",  false);
pref("network.manage-offline-status",       true);
pref("toolkit.networkmanager.disable", false);
pref("browser.startup.homepage",            "data:text/plain,browser.startup.homepage=file:///usr/share/doc/HTML/index.html");
pref("toolkit.storage.synchronous",         0);
pref("startup.homepage_override_url",       "http://www.redhat.com");
pref("startup.homepage_welcome_url",        "http://www.redhat.com");
/* Workaround for rhbz#1134876 */
pref("javascript.options.baselinejit",      false);
pref("extensions.shownSelectionUI",         true);
pref("network.negotiate-auth.allow-insecure-ntlm-v1", true);
/* Workaround for mozbz#1063315 */
pref("security.use_mozillapkix_verification", false);
