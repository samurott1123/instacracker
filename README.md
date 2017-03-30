# _Instacracker_

Instacracker is an instagram password cracker that uses tor as a proxy.

### How to use it:

*	Configure your torrc. Read the [stem faq](https://stem.torproject.org/faq.html) to understand what it means.
*	Add your tor password to the script
*	run tor
*	run the script with its arguments (-t \<number of threads>, -u \<user name>, -f \<wordlist>)
*	Wait

### Is it stable?

Not as much as I would like ;)

### Does it work?

Tests were run with 1000 wrong passwords, the 1001th was the right one and it worked.

### How long does it takes to break a password

A lot of time (sorry about that).

### Did you report it to facebook?

Yes, and they said:

Olá Luiz Guilherme,

While we understand your concern, protecting against password collection for users with weak password is unfortunately impossible. Even if we disallow multiple login attempts from the same IP (which we do, i.e. the login endpoints do have rate limit that we consider reasonable), it's trivial for an attacker to use one or more cloud service providers, open proxies, or compromised machines to enumerate passwords for weak accounts.

While we might make changes to our login endpoints' rate limits in the future, we're comfortable with the limits we have in place today, so this issue is not eligible for a bounty. We will follow up with you on any security bugs or with any further questions we may have.

Agradecemos por entrar em contato com o Facebook.


PS: A few improvements are commented but not implemented. Fell free to do it and make a pull request


		
		
