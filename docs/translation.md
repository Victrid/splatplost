# Help with translation


## How to translate the Documentation

The documentation is written in [Markdown](https://daringfireball.net/projects/markdown/), a simple markup language.

The documentation is located in the `docs` directory. The file name have postfix with code of the language. For example:

- image.md (Original, English)
- image.zh-CN.md (Chinese Simplified, PRC)
- image.ja-JP.md (Japanese, Japan)
- image.ko-KR.md (Korean, Korea)

The file name is the same as the original file, except for the postfix.

If you want to translate the documentation, you can fork this repository, translate the documentation, and then submit a pull request. Use GitHub's built-in editor to edit the file if you don't know how to use Git.

For existing translations, you can submit a pull request to fix any errors. For a new language, you can submit a pull request to add a new translation, by creating a new file with the postfix of the language code.

## How to translate the UI

**Do not modify English translation (en_US.ts). If you spotted a problem, submit an issue.**

You need to install Qt Linguist to continue. It's often bundled in Qt development tools. Check your distribution manual if you are using MacOS or Linux.

For Windows: You can download Qt, or Linguist standalone installer here: https://download.qt.io/linguist_releases/

The UI translation is located in the `splatplost/gui/i18n` directory. 

### Modify the existing translation

Open the corresponding `.ts` file with Qt Linguist, edit the translation, and save it. Then submit a pull request.

### Suggest for a new language

If you want to suggest a new language, you can start with `splatplost/gui/i18n/C.ts`. You can copy it to a new file `<Language Code>.ts`, and then translate it. Submit a pull request to add the new translation.