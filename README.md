
<div align="center">


# AIHawk: The first Jobs Applier AI Web Agent


[![LinkedIn](https://img.shields.io/badge/LinkedIn-Federico%20Elia-0A66C2?logo=linkedin&logoColor=white)](https://it.linkedin.com/in/federico-elia-5199951b6)

AIHawk's core architecture remains **open source**, allowing developers to inspect and extend the codebase. However, due to copyright considerations, we have removed all third‑party provider plugins from this repository.



---


AIHawk has been featured by major media outlets for revolutionizing how job seekers interact with the job market:

[**Business Insider**](https://www.businessinsider.com/aihawk-applies-jobs-for-you-linkedin-risks-inaccuracies-mistakes-2024-11)
[**TechCrunch**](https://techcrunch.com/2024/10/10/a-reporter-used-ai-to-apply-to-2843-jobs/)
[**Semafor**](https://www.semafor.com/article/09/12/2024/linkedins-have-nots-and-have-bots)
[**Dev.by**](https://devby.io/news/ya-razoslal-rezume-na-2843-vakansii-po-17-v-chas-kak-ii-boty-vytesnyaut-ludei-iz-protsessa-naima.amp)
[**Wired**](https://www.wired.it/article/aihawk-come-automatizzare-ricerca-lavoro/)
[**The Verge**](https://www.theverge.com/2024/10/10/24266898/ai-is-enabling-job-seekers-to-think-like-spammers)
[**Vanity Fair**](https://www.vanityfair.it/article/intelligenza-artificiale-candidature-di-lavoro)
[**404 Media**](https://www.404media.co/i-applied-to-2-843-roles-the-rise-of-ai-powered-job-application-bots/)

---

## Backend API

AIHawk includes a FastAPI backend for HTTP clients and Verity hosted audit integration.

### Start the server

```bash
pip install -r requirements.txt
python run_backend.py
```

**Local backend URL:** `http://localhost:8001` (default port; override with `BACKEND_PORT`)

- Health check: `http://localhost:8001/health`
- API docs: `http://localhost:8001/docs`
- Verity audit: `http://localhost:8001/api/v1/audit`

### Verity setup

Verity requires a **public HTTPS URL** for hosted audit integration.

1. Copy `data_folder_example/` into `data_folder/` and fill in `secrets.yaml`, `work_preferences.yaml`, and `plain_text_resume.yaml`.
2. Start the API:

```bash
pip install -r requirements.txt
python run_backend.py
```

3. Expose it publicly (Cloudflare quick tunnel):

```bash
# In a second terminal
chmod +x scripts/expose_backend.sh
./scripts/expose_backend.sh
```

Copy the `https://*.trycloudflare.com` URL into Verity as the **Backend URL**.

For production, set `BACKEND_PUBLIC_URL` to your deployed origin:

```bash
export BACKEND_PUBLIC_URL=https://your-app.example.com
python run_backend.py
```

**Verity audit behavior:** POST requests to resume endpoints without a `job_url` return `200 OK` immediately (connectivity probe). Full PDF generation runs only when `job_url` is provided.

### API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check for Verity connectivity |
| GET/POST | `/api/v1/audit` | Verity connectivity and audit status |
| GET | `/api/v1/styles` | List available resume styles |
| POST | `/api/v1/resume` | Generate base resume PDF |
| POST | `/api/v1/resume/tailored` | Generate job-tailored resume (`job_url` for full run) |
| POST | `/api/v1/cover-letter` | Generate cover letter (`job_url` for full run) |

