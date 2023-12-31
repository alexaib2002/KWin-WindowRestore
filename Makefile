JS_SCRIPTS = kwin_save.js kwin_restore.js
PY_SERVICE = plasma-windowrestore.py
SYSTEMD_CONTROLLER_SERVICE = plasma-windowrestore.service
SYSTEMD_SERVICES = $(SYSTEMD_CONTROLLER_SERVICE) plasma-windowrestore-save.service plasma-windowrestore-restore.service
SAVE_SH_PATH = $(HOME)/.config/plasma-workspace/shutdown/plasma-windowrestore-save.sh

PATH_BIN = $(HOME)/.local/bin
ifdef XDG_DATA_HOME
PATH_DATA = $(XDG_DATA_HOME)
else
PATH_DATA = $(HOME)/.local/share
endif
PATH_JS_SCRIPTS = $(PATH_DATA)/kwinrestore/scripts
PATH_LOCAL_SYSTEMD = $(HOME)/.config/systemd/user

.PHONY: all install systemd_install script_install uninstall

all: install

install: systemd_install script_install

uninstall: resource_uninstall

full_uninstall: uninstall data_remove

systemd_install: script_install
	@install -d $(PATH_LOCAL_SYSTEMD)
	@install $(SYSTEMD_SERVICES) $(PATH_LOCAL_SYSTEMD)
	@systemctl --user daemon-reload
	@echo 'systemctl --user start plasma-windowrestore-save.service' > $(SAVE_SH_PATH) && chmod +x $(SAVE_SH_PATH)
	@systemctl --user enable $(SYSTEMD_CONTROLLER_SERVICE)

script_install:
	@install -d $(PATH_BIN) $(PATH_JS_SCRIPTS)
	@install $(PY_SERVICE) $(PATH_BIN)
	@install $(JS_SCRIPTS) $(PATH_JS_SCRIPTS)

resource_uninstall:
	@rm $(SAVE_SH_PATH)
	@systemctl --user disable $(SYSTEMD_CONTROLLER_SERVICE)
	@for service in $(SYSTEMD_SERVICES); do \
		rm $(PATH_LOCAL_SYSTEMD)/$$service; \
	done
	@systemctl --user daemon-reload
	@for script in $(JS_SCRIPTS); do \
		rm $(PATH_JS_SCRIPTS)/$$script; \
	done
	@rm $(PATH_BIN)/$(PY_SERVICE)

data_remove:
	@rm -rf $(PATH_DATA)/kwinrestore
