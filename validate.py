from flask import Flask, request, jsonify
import requests
import re
import string

app = Flask(__name__)

@app.route('/validate', methods=['POST'])
def validate_place():
    data = request.get_json()
    place = data.get('place')

    if not place:
        return jsonify({"error": "No place provided"}), 400

    try:
        print(f"🔍 Validating place: {place}")

        # Wikipedia API call
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": place,
            "format": "json",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True
        }

        headers = {
            "User-Agent": "AtlasGameValidator/2.0"
        }

        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        page_id = next(iter(pages))

        if page_id == "-1":
            return jsonify({
                "place": place,
                "valid": False,
                "reason": "Wikipedia page not found"
            })

        full_extract = pages[page_id].get("extract", "").strip().lower()

        # Clean text: remove punctuation and extra spaces
        clean_text = re.sub(rf"[{string.punctuation}]", " ", full_extract)
        clean_text = re.sub(r"\s+", " ", clean_text)

        # ✅ Keywords that indicate geographic relevance
        keywords = [
            "city", "country", "town", "village", "state", "province", "district",
            "region", "territory", "capital", "municipality", "island", "continent",
            "mountain", "river", "country in", "capital of", "metropolitan", "area",
            "geographical", "located in", "place in"
        ]

        matched_keywords = [word for word in keywords if word in clean_text]
        valid = len(matched_keywords) > 0

        # ❌ Disqualify if clearly a person, profession, or fictional
        disqualifiers = [
            "was born", "fictional", "character", "king", "queen", "singer", "actor",
            "president", "emperor", "scientist", "writer", "poet", "politician",
            "footballer", "novelist", "player", "artist", "band", "musician"
        ]

        disqualified = any(term in clean_text for term in disqualifiers)

        if disqualified:
            valid = False

        return jsonify({
            "place": place,
            "valid": valid,
            "matched_keywords": matched_keywords,
            "disqualified": disqualified,
            "extract_snippet": full_extract[:300],
            "source": "Wikipedia"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5001)




# from flask import Flask, request, jsonify
# import requests
# import re
# import string

# app = Flask(__name__)

# @app.route('/validate', methods=['POST'])
# def validate_place():
#     data = request.get_json()
#     place = data.get('place')

#     if not place:
#         return jsonify({"error": "No place provided"}), 400

#     try:
#         print(f"🔍 Validating place: {place}")

#         url = "https://en.wikipedia.org/w/api.php"
#         params = {
#             "action": "query",
#             "titles": place,
#             "format": "json",
#             "prop": "extracts",
#             "exintro": True,
#             "explaintext": True
#         }

#         headers = {
#             "User-Agent": "AtlasGameValidator/1.0"
#         }

#         response = requests.get(url, params=params, headers=headers)
#         data = response.json()

#         pages = data.get("query", {}).get("pages", {})
#         page_id = next(iter(pages))

#         if page_id == "-1":
#             return jsonify({"place": place, "valid": False, "reason": "Page not found"})

#         full_extract = pages[page_id].get("extract", "").strip()
#         first_line = full_extract.split('\n')[0].lower()

#         # Clean punctuation to improve keyword matching
#         clean_line = re.sub(rf"[{string.punctuation}]", " ", first_line)

#         # ✅ Match geographic keywords
#         keywords = [
#             "city", "country", "town", "village", "state", "province", "district", "region",
#             "territory", "capital", "municipality", "island", "continent", "mountain", "river"
#         ]
#         matched_keywords = [word for word in keywords if re.search(rf"\b{word}\b", clean_line)]
#         valid = len(matched_keywords) > 0

#         # ❌ Disqualify if clearly a person or profession
#         disqualifiers = [
#             "emperor", "king", "queen", "president", "actor", "singer", "fictional",
#             "was born", "writer", "poet", "scientist", "politician", "general", "character", "novelist"
#         ]
#         if any(term in clean_line for term in disqualifiers):
#             valid = False

#         return jsonify({
#             "place": place,
#             "valid": valid,
#             "matched_keywords": matched_keywords,
#             "extract_snippet": first_line,
#             "source": "Wikipedia"
#         })

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(port=5001)


# from flask import Flask, request, jsonify
# import undetected_chromedriver as uc
# from selenium.webdriver.common.by import By
# import time

# app = Flask(__name__)

# @app.route('/validate', methods=['POST'])
# def validate_place():
#     data = request.get_json()
#     place = data.get('place')

#     if not place:
#         return jsonify({"error": "No place provided"}), 400

#     driver = None
#     try:
#         print(f"🔍 Validating place: {place}")

#         options = uc.ChromeOptions()
#         options.add_argument("--headless=new")  # ✅ safer than options.headless = True
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")

#         driver = uc.Chrome(options=options)

#         search_url = f"https://en.wikipedia.org/wiki/Special:Search?search={place}&go=Go"
#         print(f"🌐 Navigating to: {search_url}")
#         driver.get(search_url)

#         time.sleep(3)  # Allow page to load fully
#         if not driver.window_handles:
#             raise Exception("Browser window closed prematurely")

#         current_url = driver.current_url
#         title = driver.title.lower()

#         print(f"🕵️ Current URL: {current_url}, Title: {title}")

#         valid = not ("search" in title or "/w/index.php?" in current_url)

#         return jsonify({
#             "place": place,
#             "valid": valid,
#             "source": "Wikipedia"
#         })

#     except Exception as e:
#         print(f"❌ Exception occurred: {str(e)}")
#         return jsonify({"error": str(e)}), 500

#     finally:
#         if driver:
#             try:
#                 driver.quit()
#             except Exception as e:
#                 print(f"⚠️ Error closing driver: {e}")

# if __name__ == '__main__':
#     app.run(port=5001)
# from flask import Flask, request, jsonify
# import requests

# app = Flask(__name__)

# @app.route('/validate', methods=['POST'])
# def validate_place():
#     data = request.get_json()
#     place = data.get('place')

#     if not place:
#         return jsonify({"error": "No place provided"}), 400

#     try:
#         print(f"🔍 Validating place: {place}")
#         url = "https://en.wikipedia.org/w/api.php"
#         params = {
#             "action": "query",
#             "titles": place,
#             "format": "json"
#         }

#         response = requests.get(url, params=params)
#         data = response.json()

#         pages = data.get("query", {}).get("pages", {})
#         page_id = next(iter(pages))

#         valid = page_id != "-1"

#         return jsonify({
#             "place": place,
#             "valid": valid,
#             "source": "Wikipedia"
#         })

#     except Exception as e:
#         print(f"❌ Exception occurred: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# if __name__ == '__main__':
#     app.run(port=5001)
