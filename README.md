# Nuxt.js Example

This directory is a brief example of a [Nuxt.js](https://nuxtjs.org) app that can be deployed with Vercel and zero
configuration.

## Deploy Your Own

Deploy your own Nuxt.js project with Vercel.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/import/project?template=https://github.com/vercel/vercel/tree/main/examples/nuxtjs)

_Live Example: https://nuxtjs.now-examples.now.sh_

### How We Created This Example

To get started with Nuxt.js deployed with Vercel, you can use
the [Create-Nuxt-App CLI](https://www.npmjs.com/package/create-nuxt-app) to initialize the project:

```shell
$ npx create-nuxt-app my-app
```

> The only change made is to amend the output directory in `nuxt.config.js` to `"/public"`.

### 使用 Serverless Function 的方法

> 将你的程序文件放入 api 目录下，等待部署完毕后访问
> http(s)://yourDomain/api/fileName
> 就可以执行 api 目录下的 fileName.* 文件
> 具体支持哪些语言，可以看看 [Supported-Languages](https://vercel.com/docs/serverless-functions/supported-languages)
> 本仓库的语言是用的 Python

#### 关于路径

如果需要在程序文件里调用其他文件，比如我这个仓库在 cz_ip/ip_data.py 里调用了 cz_ip/ip.dat 那就需要注意路径问题, 即使你两个文件(调用文件与被调用文件)放同一个目录,那也得使用绝对路径引用
例如:
```python
open('./cz_ip/ip.dat')
```
而不能
```python
open('ip.dat')
```
### 题外话
这个 Serverless Function 貌似对 Python 支持不是很好，至少没办法通过 
BaseHTTPRequestHandler 类 的 client_address 字段来获取用户 IP，查看它的 Serverless Function 调用日志 只发现几行大字
```
127.0.0.1 - - [04/Jun/2021 02:19:22] "GET /api/api HTTP/1.1 " 200 -
```
至少是没办法使用 Python 获取用户 IP 的