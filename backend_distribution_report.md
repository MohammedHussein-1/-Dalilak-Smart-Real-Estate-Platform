# Backend Workload Distribution: Detailed Technical Report

This report provides a granular breakdown of backend responsibilities for the Real Estate platform, including direct references to models, database fields, and code sections in `app.py`.

---

### **1. Infrastructure, Database & Security Lead**
**Primary Focus**: System foundation, data integrity, and cross-cutting security.

*   **Database Architecture**: Ownership of `models.py`.
    *   **Admin Tasks**: Maintenance of the `User` role field (`models.py:18`) and ensuring data consistency across relationships.
    *   **Migrations**: Managing the `init_db` function in `app.py` (approx. lines 581-630).
*   **Security & Environment**:
    *   **Auth Logic**: Password hashing methods in `models.py` (lines 36-40).
    *   **App Config**: Environment variable management in `app.py` (lines 11-20).
*   **Key Files**: `models.py`, `reset_db.py`, `.env`.

### **2. User Lifecycle & Verification Architect**
**Primary Focus**: Identity management and administrative oversight.

*   **Authentication & Access**:
    *   **Flows**: Login (`app.py`: lines 263-294) and Signup (`app.py`: lines 295-316) logic.
    *   **RBAC**: Protecting admin-only routes using `current_user.role != 'admin'`.
*   **Identity Verification System**:
    *   **Backend Logic**: Implementation of `/submit-verification` (`app.py`: lines 369-428).
    *   **Data Structure**: Handling `User` verification fields such as `verification_status`, `id_front_url`, and `id_back_url` (`models.py`: lines 20-28).
*   **Admin Dashboard Logic**:
    *   **Stats API**: Fetching system-wide statistics (`app.py`: lines 317-349).
    *   **Moderation API**: User verification actions (`app.py`: lines 531-550).
*   **Key Files**: `app.py`, `templates/verify.html`, `templates/admin.html`.

### **3. Property Ecosystem & Search Expert**
**Primary Focus**: Core product features and map integration.

*   **Listing Lifecycle**:
    *   **Ingestion**: Property submission logic (`app.py`: lines 429-505).
    *   **DB Model**: Managing the `Property` model (`models.py`: lines 42-83) and `PropertyImage` relationship (`models.py`: lines 84-88).
    *   **Approval Flow**: Admin property review (`app.py`: lines 507-530).
*   **Discovery & Maps**:
    *   **Search Engine**: Filtering logic in `/map` and home views (`app.py`: lines 73-112).
    *   **Geospatial Data**: Handling `lat` and `lng` coordinates for the map interface.
*   **Key Files**: `app.py`, `models.py`, `data.py`.

### **4. AI Intelligence & Advanced Features Engineer**
**Primary Focus**: AI interactions and user engagement.

*   **Conversational AI (Dalilak)**:
    *   **Implementation**: LangChain logic in `chatbot.py`.
    *   **Integration**: Chat API endpoint in `app.py` (lines 557-580).
*   **User Engagement Features**:
    *   **Persistence**: Implementing `/toggle_save` logic (`app.py`: lines 191-203) and using the `saved_properties` association table (`models.py`: lines 8-11).
    *   **Automation**: Development of `SavedSearch` (`models.py`: lines 89-95) and `SearchAlert` (`models.py`: lines 96-103) functionality.
*   **Key Files**: `chatbot.py`, `app.py`, `models.py`.

---

### **Database Summary for Team Use**

| Model | Assigned Lead | Core Fields of Note |
| :--- | :--- | :--- |
| `User` | **Lead 2** | `email`, `role`, `verification_status`, `id_front_url`. |
| `Property` | **Lead 3** | `title`, `price`, `lat`, `lng`, `status` (pending/approved). |
| `PropertyImage` | **Lead 3** | `image_url`, `property_id`. |
| `SavedSearch` | **Lead 4** | `user_id`, `filters` (JSON type). |
| `SearchAlert` | **Lead 4** | `criteria`, `frequency`, `is_active`. |

---

> [!NOTE]
> Each team member's role covers a logical "vertical" slice of the database and API. This minimizes the risk of merge conflicts while ensuring dedicated expertise in each area.
