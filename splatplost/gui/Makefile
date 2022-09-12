update_translation:
	rm -f i18n/C.ts
	pylupdate6 ./*.py ./*.ui --ts i18n/C.ts
	pylupdate6 ./*.py ./*.ui --ts i18n/zh_CN.ts
	pylupdate6 ./*.py ./*.ui --ts i18n/zh_TW.ts
	pylupdate6 ./*.py ./*.ui --ts i18n/ja_JP.ts
	pylupdate6 ./*.py ./*.ui --ts i18n/en_US.ts

create_qm:
	lrelease i18n/*.ts

clean_qm:
	rm i18n/*.qm
