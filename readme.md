# Careless Leak Lookup

<!-- ![google-dark](./google-dark.jpeg) -->

## Overview

Careless Leak Lookup is a **simple reverse phone lookup** ;
that is, a tool to obtain information about the subscriber (owner) of the phone number.

Please read [Disclaimer](#disclaimer), [Is the user notified about this ?](#is-the-user-notified-about-this-) and [Is it legal ?](#is-it-legal-).


This tool takes advantage of the unattentive leaked/published data.
The output typically consists of social media profiles.

## Disclaimer

This project is intended for educational and lawful purposes only. The primary goal is to provide users with a platform to learn and experiment with various technologies, programming languages, and security concepts in a controlled environment. The creators and contributors of this project do not endorse or support any malicious activities, including but not limited to hacking, unauthorized access, or any form of cybercrime.

Users are expected to use this project responsibly and in compliance with applicable laws and regulations. Unauthorized use of this project for any malicious or illegal activities is strictly prohibited. The creators and contributors disclaim any responsibility for any misuse or damage caused by the use of this project for unauthorized and unlawful purposes.

It is essential to respect the privacy and security of others and obtain explicit permission before attempting to access or modify any system or data. Any actions performed with the knowledge gained from this project should be conducted in an ethical manner, with a focus on enhancing cybersecurity/privacy awareness and promoting responsible use of technology.

By using this project, you acknowledge and agree to abide by the principles outlined in this disclaimer. If you do not agree with these terms, you are not authorized to use or contribute to this project.

## Setup

### Pip install
```sh
sudo apt install tesseract-ocr # required
pip3 install careless-leak
```

#### Manual install
```sh
sudo apt install tesseract-ocr # required

git clone https://github.com/EternalDreamer01/careless-leak.git
cd careless-leak

pip3 install -r requirements-min.txt # for minimal, manual searching
# OR
pip3 install -r requirements.txt # automatic searching
```

### Prerequisites

* Python 3.8+
* `tesseract-ocr`

### Setup automatic searching

Create `.env` file with ;
```toml
LINKEDIN_EMAIL=<your-email>
LINKEDIN_PASSWORD=<your-password>
```

## Usage

__Supports international phone format only__
```sh
$ ./c3l.py "+44 808 157 0192"
```

## FAQ

### Is the user notified about this ?
**It's possible** that the user is notified you visited their profile, especially on LinkedIn.
You can pass the `-a`/`--anonymous` argument to avoid logging in anywhere, but results may be incomplete; it's equivalent to not setting any environment variables.

### Is it legal ?
It's legal to view publicly or freely available information, when the user is aware of this feature and consented to it.

However, the constant storage of this data could be considered a privacy violation (mainly for EU).
You alone bear full responsibility for any misuse or damage resulting from the unauthorized or unlawful use of this project.

## How it works
This tools takes advantages of Google Dorks ;
1. **manual mode** would simply open the results on your default browser,
2. **automatic mode** would use selenium for browser interaction and, tesseract for text extraction from images :

* It would first look at the images, extract their text in an attempt to find the phone number,
* Then, it would look at *All* results (links), where  :
	* LinkedIn links are inspected in depth through their posts
	* For any other, it inspect the document directly available through Google to inspect title and description


__Tested and confirmed functioning for:__
* [x] LinkedIn: Posts (text) and phone extraction from photos/CV (image)
* [x] Instagram: Profile description (text)
* [ ] ~~Facebook: posts (text), comments (text)~~
* [ ] ~~Reddit~~
* [ ] ~~Twitter~~
* [ ] ~~GitHub~~
* [ ] ~~Quora~~


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

If you encounter an issue about a phone number not found while it should, or a noticeable social media that isn't scanned, feel free to open an issue as well.

## License

[LGPL-3.0 or later](LICENSE)
