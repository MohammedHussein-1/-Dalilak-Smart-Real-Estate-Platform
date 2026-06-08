import re

class RealEstateChatbot:
    def __init__(self, properties_data):
        self.properties = properties_data or []
        self.city_synonyms = {
            "badr": ["بدر", "مدينة بدر", "badr", "badr city"],
            "el shorouk": ["الشروق", "شروق", "el shorouk", "shorouk", "shorouk city"],
            "new administrative capital": ["العاصمة الإدارية", "العاصمة الادارية", "new administrative capital", "new capital", "capital"],
            "nasr city": ["مدينة نصر", "مدينه نصر", "nasr city", "nasr"],
        }
        self.city_display = {
            "badr": "بدر",
            "el shorouk": "الشروق",
            "new administrative capital": "العاصمة الإدارية",
            "nasr city": "مدينة نصر",
            "new cairo": "القاهرة الجديدة",
        }
        self.available_cities = sorted({(p.get('city') or '').strip() for p in self.properties if p.get('city')})
        self.city_lookup = {}
        self._build_city_lookups()
        self.yes_words = {"نعم", "ايوه", "أيوه", "أجل", "تمام", "yes", "ok", "okay"}
        self.greet_words = ["مرحبا", "مرحباً", "أهلا", "اهلا", "hi", "hello"]
        self.thanks_words = ["شكرا", "شكر", "merci", "thanks", "thank you"]
        self.goodbye_words = ["مع السلامة", "وداعا", "وداعاً", "سلام", "bye", "goodbye"]
        self.help_words = ["مساعدة", "help", "تساعدني", "كيف", "ايه تقدر"]
        self.search_words = ["ابحث", "أبحث", "عايز", "عاوزه", "محتاج", "ادور", "دور", "ترشيح", "اقتراح"]
        self.rent_words = ["ايجار", "إيجار", "rent", "استئجار"]
        self.buy_words = ["شراء", "بيع", "تمليك", "buy", "sale"]
        self.property_type_map = {
            "apartment": ["شقة", "شقه", "apartment", "flat"],
            "villa": ["فيلا", "villa"],
            "studio": ["استوديو", "studio"],
            "duplex": ["دوبلكس", "duplex"],
            "townhouse": ["تاون هاوس", "townhouse"],
            "chalet": ["شاليه", "chalet"],
            "office": ["مكتب", "office", "تجاري", "commercial"],
            "land": ["أرض", "ارض", "land"],
        }
        self.sort_words = {
            "cheap": ["ارخص", "أرخص", "الأرخص", "cheap"],
            "expensive": ["اغلى", "أغلى", "الأغلى", "expensive"],
            "newest": ["الأحدث", "جديد", "newest"],
        }

    def _build_city_lookups(self):
        for canonical, synonyms in self.city_synonyms.items():
            for alias in synonyms:
                self.city_lookup[alias.lower()] = canonical
        for city in self.available_cities:
            normalized = city.strip().lower()
            if normalized and normalized not in self.city_lookup:
                self.city_lookup[normalized] = normalized
                if normalized not in self.city_display:
                    self.city_display[normalized] = city
            if " " in normalized:
                self.city_lookup[normalized.replace(" ", "")] = normalized
                self.city_lookup[normalized.replace(" ", "-")] = normalized

    def _find_city_in_text(self, text):
        if not text:
            return None
        for alias, canonical in self.city_lookup.items():
            if alias in text:
                return canonical
        return None

    def _get_city_suggestions(self, language='ar'):
        if not self.available_cities:
            if language == 'ar':
                return "حاليًا لا توجد مدن متاحة في النظام. من فضلك أضف بعض العقارات أولاً."
            return "There are currently no cities available. Please add some properties first."
        first_cities = self.available_cities[:5]
        if language == 'ar':
            return "يمكنني أن أساعدك في المدن التالية: " + ", ".join(first_cities) + "."
        return "I can help you with these cities: " + ", ".join(first_cities) + "."

    def _is_suggestion_request(self, text):
        suggestion_words = ["اقترح", "اقتراح", "suggest", "recommend", "help me choose", "what's best"]
        return any(word in text for word in suggestion_words)

    def _get_best_properties_summary(self, language='ar', max_items=3):
        sorted_props = sorted(
            self.properties,
            key=lambda p: int(re.sub(r"\D", "", str(p.get('price') or '') or "0"))
            if re.search(r"\d", str(p.get('price') or '')) else 0
        )
        selected = sorted_props[:max_items]
        if not selected:
            return ""
        if language == 'ar':
            lines = [f"- {p.get('title')} في {p.get('city')} بسعر {p.get('price')}" for p in selected]
            return "إليك بعض الخيارات المتاحة:\n" + "\n".join(lines)
        lines = [f"- {p.get('title')} in {p.get('city')} for {p.get('price')}" for p in selected]
        return "Here are some available options:\n" + "\n".join(lines)

    def get_response(self, history, text, language=None):
        language = language or ('ar' if re.search(r'[\u0600-\u06FF]', text or '') else 'en')
        text = (text or "").strip().lower()
        history = history or []

        if self._is_suggestion_request(text):
            return self._get_city_suggestions(language) + "\n" + self._get_best_properties_summary(language)

        messages = {
            'greet': {
                'ar': "مرحباً! 👋 أنا دليلك. قلّي المدينة ونوع العقار والميزانية، وأنا أرتّب لك أفضل الخيارات.",
                'en': "Hello! 👋 I'm Dalilak. Tell me the city, property type, and budget — I'll find the best options for you."
            },
            'thanks': {
                'ar': "العفو! إذا تحب نكمل، قلّي المدينة والميزانية ونوع العقار.",
                'en': "You're welcome! If you'd like to continue, tell me the city, budget, or property type."
            },
            'goodbye': {
                'ar': "سعيد بالتعامل معك! لو احتجت أي مساعدة رجّعلي في أي وقت.",
                'en': "It was a pleasure helping you! Come back anytime."
            },
            'help': {
                'ar': "أقدر أساعدك في البحث عن عقارات (شراء/إيجار) وتصفية النتائج بالمدينة والميزانية وعدد الغرف. مثال: شقة للبيع في بدر بحد أقصى 2 مليون، 3 غرف.",
                'en': "I can help you search for properties (buy/rent) and filter by city, budget, and rooms. Example: apartment for rent in Cairo under 15,000 EGP, 2 bedrooms."
            },
            'ask_more': {
                'ar': "تمام! أي مدينة؟ وهل تفضل شراء أم إيجار؟ ولو عندك ميزانية أو عدد غرف، اذكرهم.",
                'en': "Great! Which city? And do you want to buy or rent? Include your budget or number of rooms if you have them."
            },
            'no_filter': {
                'ar': "أقدر أساعدك في البحث عن عقار أو الإجابة عن أسئلة تخص العقارات. جرّب تسألني عن مدينة أو ميزانية.",
                'en': "I can help you search for properties or answer real estate questions. Try asking about a city or your budget."
            },
            'not_found': {
                'ar': "لم أجد نتائج مطابقة تماماً. جرّب تحديد المدينة أو الميزانية أو نوع العقار.",
                'en': "No exact matches found. Try specifying a city, budget, or property type."
            },
            'missing': {
                'ar': "من فضلك اكتب رسالة أولاً.",
                'en': "Please enter a message first."
            }
        }

        if not text:
            return messages['missing'][language]

        if any(word in text for word in self.greet_words):
            return messages['greet'][language]

        if any(word in text for word in self.thanks_words):
            return messages['thanks'][language]

        if any(word in text for word in self.goodbye_words):
            return messages['goodbye'][language]

        if any(word in text for word in self.help_words):
            return messages['help'][language]

        if text in self.yes_words:
            filters = self._extract_filters_from_history(history)
            if not self._has_any_filter(filters):
                return messages['ask_more'][language]
            results = self._filter_results(filters)
            return self._format_results(results, filters, language)

        current_filters = self._extract_filters(text)
        history_filters = self._extract_filters_from_history(history)
        filters = self._merge_filters(current_filters, history_filters)

        if not self._has_any_filter(filters):
            if any(word in text for word in self.search_words):
                return messages['ask_more'][language]
            return messages['no_filter'][language]

        results = self._filter_results(filters)
        if results:
            return self._format_results(results, filters, language)

        if filters.get("city") and not results:
            city_label = self.city_display.get(filters["city"], filters["city"])
            if language == 'ar':
                return f"عذراً، لا يوجد عقارات متاحة حالياً في {city_label}. جرّب تغيير الميزانية أو نوع العقار."
            return f"Sorry, no available properties in {city_label} right now. Try adjusting the budget or property type."

        return messages['not_found'][language]

    def _extract_content(self, msg):
        if isinstance(msg, dict):
            return str(msg.get("content") or msg.get("message") or "")
        return str(msg)

    def _extract_filters_from_history(self, history):
        filters = {
            "city": None, "listing_type": None, "property_type": None,
            "min_price": None, "max_price": None, "bedrooms": None, "sort": None,
        }
        for msg in reversed(history):
            content = self._extract_content(msg).lower()
            partial = self._extract_filters(content)
            for key, value in partial.items():
                if filters.get(key) is None and value is not None:
                    filters[key] = value
            if self._has_any_filter(filters):
                break
        return filters

    def _find_property_type(self, text):
        for canonical, synonyms in self.property_type_map.items():
            for s in synonyms:
                if s in text:
                    return canonical
        return None

    def _find_sort(self, text):
        for sort_key, words in self.sort_words.items():
            if any(w in text for w in words):
                return sort_key
        return None

    def _extract_bedrooms(self, text):
        match = re.search(r"(\d+)\s*(غرف|غرفة|bed|beds)", text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None

    def _extract_price_range(self, text):
        numbers = []
        for m in re.finditer(r"\d+(?:[.,]\d+)?", text):
            raw = m.group(0).replace(",", "")
            try:
                value = float(raw)
            except ValueError:
                continue
            window = text[max(0, m.start() - 6): m.end() + 10]
            if "مليون" in window or "million" in window:
                value *= 1_000_000
            elif "ألف" in window or "الف" in window or "k" in window:
                value *= 1_000
            numbers.append(int(value))

        if not numbers:
            return None, None

        if len(numbers) >= 2 and ("الى" in text or "إلى" in text or "-" in text or "between" in text):
            low, high = sorted(numbers[:2])
            return low, high

        single = numbers[0]
        if "اقل" in text or "أقل" in text or "تحت" in text or "حتى" in text:
            return None, single
        if "اكبر" in text or "أكبر" in text or "فوق" in text or "على الأقل" in text:
            return single, None

        return None, single

    def _normalize_listing_type(self, value):
        if not value:
            return ""
        v = str(value).lower()
        if v in {"rent", "rental", "lease", "ايجار", "إيجار"}:
            return "rent"
        if v in {"buy", "sale", "sell", "شراء", "بيع", "تمليك"}:
            return "buy"
        return v

    def _price_to_int(self, price_text):
        if price_text is None:
            return None
        matches = re.findall(r"\d+", str(price_text))
        if not matches:
            return None
        try:
            return int("".join(matches))
        except ValueError:
            return None

    def _matches_property_type(self, p, desired_type):
        if not desired_type:
            return True
        prop_type = str(p.get("property_type", "")).lower()
        if prop_type and prop_type == desired_type:
            return True
        hay = " ".join([str(p.get("title", "")), str(p.get("description", ""))]).lower()
        for synonym in self.property_type_map.get(desired_type, []):
            if synonym in hay:
                return True
        return False

    def _filter_results(self, filters):
        results = []
        city_filter = filters.get("city")
        listing_type_filter = filters.get("listing_type")
        property_type_filter = filters.get("property_type")
        min_price = filters.get("min_price")
        max_price = filters.get("max_price")
        bedrooms = filters.get("bedrooms")

        for p in self.properties:
            city = str(p.get("city", "")).lower()
            city_key = self._find_city_in_text(city) or city
            if city_filter and city_key != city_filter:
                continue

            listing_type = self._normalize_listing_type(p.get("listing_type"))
            if listing_type_filter and listing_type != listing_type_filter:
                continue

            if not self._matches_property_type(p, property_type_filter):
                continue

            price_num = self._price_to_int(p.get("price"))
            if min_price and price_num is not None and price_num < min_price:
                continue
            if max_price and price_num is not None and price_num > max_price:
                continue

            if bedrooms is not None:
                try:
                    prop_beds = int(p.get("bedrooms", 0) or 0)
                except ValueError:
                    prop_beds = 0
                if prop_beds < bedrooms:
                    continue

            results.append(p)

        sort_key = filters.get("sort")
        if sort_key in {"cheap", "expensive"}:
            results.sort(
                key=lambda r: self._price_to_int(r.get("price")) or 0,
                reverse=(sort_key == "expensive")
            )

        return results

    def _format_results(self, results, filters, language='ar'):
        if not results:
            if language == 'ar':
                return "عذراً، لا يوجد عقارات متاحة حالياً في هذا النطاق."
            return "Sorry, there are no available properties in that range right now."
        summary = []
        for r in results[:3]:
            title = r.get("title", "عقار" if language == 'ar' else "Property")
            price = r.get("price", "")
            city = r.get("city", "")
            details = " - ".join([s for s in [title, price, city] if s])
            summary.append(details)
        hint = (
            " لو تحب فلترة أكثر، قلّي الميزانية أو عدد الغرف."
            if language == 'ar'
            else " For more filtering, tell me your budget or preferred number of rooms."
        )
        if filters.get("city"):
            city_label = self.city_display.get(filters["city"], filters["city"])
            if language == 'ar':
                return f"✨ أفضل نتائج في {city_label}: " + " | ".join(summary) + hint
            return f"✨ Best matches in {city_label}: " + " | ".join(summary) + hint
        return ("✨ أفضل النتائج: " if language == 'ar' else "✨ Best matches: ") + " | ".join(summary) + hint

    def _extract_filters(self, text):
        city = self._find_city_in_text(text)
        listing_type = None
        if any(word in text for word in self.rent_words):
            listing_type = "rent"
        if any(word in text for word in self.buy_words):
            listing_type = "buy"

        property_type = self._find_property_type(text)
        min_price, max_price = self._extract_price_range(text)
        bedrooms = self._extract_bedrooms(text)
        sort = self._find_sort(text)

        return {
            "city": city,
            "listing_type": listing_type,
            "property_type": property_type,
            "min_price": min_price,
            "max_price": max_price,
            "bedrooms": bedrooms,
            "sort": sort,
        }

    def _merge_filters(self, current_filters, history_filters):
        merged = dict(current_filters)
        for key in ["city", "listing_type", "property_type", "min_price", "max_price", "bedrooms", "sort"]:
            if merged.get(key) is None and history_filters.get(key) is not None:
                merged[key] = history_filters[key]
        return merged

    def _has_any_filter(self, filters):
        return any(filters.get(k) is not None for k in [
            "city", "listing_type", "property_type", "min_price", "max_price", "bedrooms"
        ])
