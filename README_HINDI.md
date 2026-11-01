# सीकर सर्विस — MVP (सीकर, राजस्थान)

यह मोबाइल-फ्रेंडली, installable PWA + backend starter है। इसमें:
- ग्राहक सर्विस बुकिंग फॉर्म
- सर्विस पार्टनर आवेदन
- SQLite डेटाबेस में बुकिंग और आवेदन सेव
- पासवर्ड-सुरक्षित बेसिक एडमिन पैनल
- बुकिंग/पार्टनर स्टेटस अपडेट
- मोबाइल होम स्क्रीन पर जोड़ने योग्य PWA manifest/service worker

## स्थानीय कंप्यूटर पर चलाएँ
Python 3.10+ आवश्यक है।

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

पासवर्ड सेट करके चलाएँ:
- Mac/Linux:
  `export ADMIN_PASSWORD='अपना-मजबूत-पासवर्ड'`
  `export SECRET_KEY='एक-लंबी-रैंडम-सीक्रेट-वैल्यू'`
  `python app.py`
- Windows PowerShell:
  `$env:ADMIN_PASSWORD='अपना-मजबूत-पासवर्ड'`
  `$env:SECRET_KEY='एक-लंबी-रैंडम-सीक्रेट-वैल्यू'`
  `python app.py`

फिर `http://127.0.0.1:5000` खोलें। एडमिन पैनल `http://127.0.0.1:5000/admin` पर है।

## इसे ग्राहकों के लिए इंटरनेट पर चालू करना
इस फ़ोल्डर को HTTPS सपोर्ट वाले Python hosting provider पर deploy करना होगा। `ADMIN_PASSWORD` और `SECRET_KEY` को hosting के environment variables में सेट करें। `DATABASE_PATH` को persistent disk पर रखें, ताकि deploy/restart के बाद डेटा न मिटे। Host पर start command `gunicorn app:app` हो सकती है; उसके लिए `gunicorn` को requirements.txt में जोड़ें (यह फ़ाइल अभी development run के लिए है)।

## ज़रूरी सीमा
यह अभी production-ready marketplace नहीं है। इसमें OTP login, online payments, automatic SMS/WhatsApp notifications, provider assignment, customer/partner accounts, backups, audit logs और full security review शामिल नहीं हैं। HTTPS hosting और configuration के बिना इसे सार्वजनिक ग्राहकों के लिए लॉन्च न करें। मोबाइल पर installable PWA के लिए वेबसाइट HTTPS पर उपलब्ध होनी चाहिए।

## लॉन्च से पहले जोड़ना होगा
1. आधिकारिक संपर्क/WhatsApp नंबर और सेवा क्षेत्र की पुष्टि
2. कमीशन और पार्टनर मासिक फीस की लिखित नीति
3. प्राइवेसी पॉलिसी/Terms और ग्राहक सहमति
4. OTP/anti-spam, database backups, secure hosting, monitoring
5. बुकिंग रद्द/रिफंड और शिकायत प्रक्रिया


## Render पर deploy करने की तैयारी
इस प्रोजेक्ट में `render.yaml` और `Procfile` जोड़े गए हैं। `render.yaml` persistent disk के लिए कॉन्फ़िगर है; Render पर इस प्रकार के persistent disk/instance के लिए शुल्क लग सकता है। बिना persistent storage के SQLite में सेव ग्राहक बुकिंग deploy/restart के बाद खो सकती हैं।

1. ZIP को अपने कंप्यूटर पर extract करें।
2. प्रोजेक्ट को अपने GitHub repository में upload करें।
3. Render में GitHub connect करके repository चुनें और Blueprint deploy करें।
4. Render की सेटिंग में `ADMIN_PASSWORD` के लिए मजबूत पासवर्ड डालें।
5. deploy के बाद वेबसाइट URL खोलकर test booking करें, फिर `/admin` खोलकर admin login जाँचें।
6. सार्वजनिक लॉन्च से पहले privacy policy, terms, contact/WhatsApp, backups और सुरक्षा जाँच जोड़ें।

मैं आपकी ओर से किसी होस्टिंग खाते में लॉगिन या भुगतान नहीं कर सकता। वेबसाइट को वास्तव में live करने के लिए आपके hosting account में deployment और configuration की अनुमति/कार्रवाई ज़रूरी है।
