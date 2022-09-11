# 帮助翻译


## 如何翻译文档

文档是用[Markdown](https://daringfireball.net/projects/markdown/)写的，这是一种简单的标记语言。

文档位于`docs`目录中。文件名有语言代码的后缀。例如。

- image.md (原文，英文)
- image.zh-CN.md (简体中文，中华人民共和国)
- image.ja-JP.md (日语，日本)
- image.ko-KR.md (韩文，韩国)

除了后缀外，文件名与原始文件相同。

如果你想翻译文档，你可以Fork这个仓库，翻译文档，然后提交一个Pull Request。如果你不知道如何使用Git，可以使用GitHub的内置编辑器来编辑文件。

对于现有的翻译，你可以提交一个Pull Request来修复任何错误。对于一个新的语言，你可以提交一个Pull Request，通过创建一个带有语言代码后缀的新文件来添加一个新的翻译。

## 如何翻译用户界面

**不要修改英文翻译（en_US.ts）。如果你发现了问题，请提交一个issue。**

你需要安装Qt Linguist才能继续。它通常被捆绑在Qt开发工具中。如果你使用的是MacOS或Linux，请查看你的发行版手册。

对于Windows。你可以下载Qt，或在这里Linguist独立安装程序：https://download.qt.io/linguist_releases/

UI翻译位于`splatplost/gui/i18n`目录下。

### 修改现有的翻译

用Qt Linguist打开相应的`.ts`文件，编辑翻译，并保存它。然后提交一个Pull Request。

### 建议一门新的语言

如果你想建议一个新的语言，你可以从`splatplost/gui/i18n/C.ts`开始。你可以把它复制到一个新的文件`<语言代码>.ts`，然后翻译它。提交一个Pull Request来添加新的翻译。