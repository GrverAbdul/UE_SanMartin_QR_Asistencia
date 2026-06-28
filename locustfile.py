from locust import HttpUser, task, between
import re

class AsistenciaUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # 1. GET login → token CSRF + cookie CSRF
        response = self.client.get("/usuarios/login/")
        print(f"[GET /login] status={response.status_code}")

        match = re.search(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']', response.text)
        if match:
            self.csrf_token = match.group(1)
        else:
            print("[CSRF] Token HTML no encontrado")
            return

        if 'csrftoken' in response.cookies:
            self.csrf_cookie = response.cookies['csrftoken']
        else:
            print("[CSRF] No cookie CSRF")
            return

        # 2. POST login SIN seguir redirección
        headers = {
            'Referer': 'https://ue-sanmartin-qr-asistencia.onrender.com/usuarios/login/',
            'Origin': 'https://ue-sanmartin-qr-asistencia.onrender.com',
        }
        login_data = {
            "csrfmiddlewaretoken": self.csrf_token,
            "username": "admin",
            "password": "123"
        }
        response = self.client.post(
            "/usuarios/login/",
            data=login_data,
            cookies={'csrftoken': self.csrf_cookie},
            headers=headers,
            allow_redirects=False   # <--- ¡clave!
        )
        print(f"[POST /login] status={response.status_code} Location={response.headers.get('Location')}")

        # Extraer sessionid de la respuesta 302
        if response.status_code == 302:
            set_cookie = response.headers.get('Set-Cookie', '')
            print(f"[POST /login] Set-Cookie: {set_cookie}")
            match = re.search(r'sessionid=([^;]+)', set_cookie)
            if match:
                self.session_cookie = match.group(1)
                print("[SESSION] Cookie extraída de redirección")
            else:
                print("[SESSION] No sessionid en Set-Cookie")
                self.session_cookie = None
        else:
            # Si no hubo redirección, probar en cookies de la respuesta
            if 'sessionid' in response.cookies:
                self.session_cookie = response.cookies['sessionid']
            else:
                self.session_cookie = None

        # 3. Seguir la redirección manualmente para activar la sesión
        if self.session_cookie:
            redirect_url = response.headers.get('Location', '/')
            self.client.get(redirect_url, cookies={'sessionid': self.session_cookie, 'csrftoken': self.csrf_cookie})
            print("[SESSION] Sesión activada")

    @task(5)
    def escanear_qr(self):
        if not self.csrf_token or not self.session_cookie:
            return
        headers = {
            'X-CSRFToken': self.csrf_token,
            'Referer': 'https://ue-sanmartin-qr-asistencia.onrender.com/asistencia/escaner/',
            'Origin': 'https://ue-sanmartin-qr-asistencia.onrender.com',
        }
        cookies = {
            'sessionid': self.session_cookie,
            'csrftoken': self.csrf_cookie
        }
        response = self.client.post(
            "/asistencia/registrar_qr/",
            json={"qr_id": ["a03a6a8f-7c0a-4a71-87b6-7a7aad65021e", "4dfd9125-76ce-4c29-8bfb-7262197b10e7", 
                            "bda7f09f-b514-4582-bc03-3b9731aca9ad", "593f7167-2871-4859-a507-3c72ce256468", 
                            "8ee32a0e-7df1-45f8-babd-b4443c0405e2", "342aafc7-a9d2-4462-9640-5a084bac9c2b", 
                            "92243ae1-686b-4c78-9a42-6ee78cda9fbf", "32617edc-16cc-4eb4-b093-328b6a022025", 
                            "35ec1959-659e-4266-b960-d6c5ac5209a1", "a24ae84f-e521-4b67-993e-0a11514945f9", 
                            "02f705f9-cdcd-46e0-88f5-8098e4bb2c24", "82325d56-4d48-495b-9403-8c60ef06a0d7", 
                            "1833a9e6-1a08-415c-82a0-5428307bac81", "bb119964-63bd-4f10-a61c-88a8df71e36d", 
                            "4df1df54-f6c2-40e4-be18-5ce6884a2c38", "ba9e0a55-b0ee-4a7b-b994-99012d0f94ab", 
                            "b5060390-2670-484d-a77f-de4d6d0bf20d", "2fbf41d0-9f37-4556-821d-200a31863fad", 
                            "8defa2f5-9561-4bab-a83c-3748697731ce", "9c7b4314-5abb-470b-9e8d-a3f2fa433121", 
                            "52dbfc2c-e169-43d8-b4dd-ac29837208e2", "96f30471-4a17-4d1a-91eb-0a21cb73872b", 
                            "aab9f0ba-6583-4668-aa82-9eed6cf6c23e", "ee09ceb4-081f-40ac-9253-341d5da8736b", 
                            "610345c0-6f4d-43e2-b790-49c158013422", "20926402-bea4-4812-aba7-d670133723e6", 
                            "f5c0e3cb-b3cb-4a78-a18b-938f578cad1f", "cbf615c2-faab-44f1-812c-b4966c93f93b", 
                            "353175fa-736d-4dd0-bb5c-8368c8412a22", "e44edae4-d79b-4c27-bc21-bcfee6cb7c40", 
                            "0ae4548b-3dc1-41c4-8e40-a78a57edfc6c", "2a14170c-3670-4547-a9fc-c88653ba2d0d", 
                            "4bad688a-bde6-42b0-a8ef-3b6f83346ee8", "d6e30156-e470-4fc5-b568-c77faaafdf92", 
                            "4fe406bd-c39b-4705-859b-bbb21e5e8644", "1d327c82-e86c-4db1-ab8e-7e6689ec5dbd", 
                            "fc87d9f5-0edb-4dfa-b425-d867035b6b0e", "836c6ce2-fc21-4878-b2f4-4f1e1a1ad50b", 
                            "2f9426f7-82b9-48eb-816a-7ba7dba4a109", "75cf5c44-3e73-4176-964b-62420767d2b4", 
                            "52e91158-864e-438b-9641-6cfb1ff6915e", "603ed6a7-f85a-49bc-a50c-0636a06501f0", 
                            "c9a102cd-fe04-4c17-aa16-1b5ae3d6718c", "10367789-deab-4778-be36-a9bf6ab0c9a4", 
                            "574fa336-2c08-40b8-a124-2fafaae86596", "c9e963ce-42b3-427b-95ed-5458a1f05fe6", 
                            "4b31ee88-96a1-4af3-a7bb-ee14c9c00b12", "92fb3727-93ae-41be-9a28-bfb639c0bafb", 
                            "c56ca4c4-dd6e-4a9c-bcd5-761cf1c021b3", "7469a3a4-e1fa-43a9-95ec-03c4fac359c1", 
                            "1dc0c2a2-c07d-4043-a9d7-a55b5ecb8328", "c1a330d3-1b7e-4790-9039-97c283bf2c6d"]},
            headers=headers,
            cookies=cookies
        )
        print(f"[POST /registrar_qr] status={response.status_code}")

    @task(2)
    def historial(self):
        if not self.session_cookie:
            return
        cookies = {'sessionid': self.session_cookie}
        response = self.client.get("/asistencia/historial/", cookies=cookies)
        print(f"[GET /historial] status={response.status_code}")