# AI Life Admin - Complete Email Workflow

## 📧 Complete Email System Flow

### 1. **Email Account Connection (OAuth Flow)**

#### Step 1: User Clicks "Connect Account"
- **Frontend**: `EmailInbox.tsx` → User clicks "Connect Account" button
- **Action**: Opens modal with Gmail/Outlook/IMAP options

#### Step 2: OAuth Authorization
- **Frontend**: Calls `GET /api/v1/emails/oauth/gmail/authorize`
- **Backend**: `emails.py` → `gmail_oauth_authorize()`
  - Generates secure state token
  - Creates OAuth URL with:
    - Client ID & Secret (from `.env`)
    - Redirect URI: `http://localhost:5173/emails/oauth/callback`
    - Scopes: `gmail.readonly` + `userinfo.email`
  - Returns authorization URL
- **Frontend**: Redirects user to Google login page

#### Step 3: User Authorizes
- User logs in to Google
- User grants permissions
- Google redirects back with `code` and `state` parameters

#### Step 4: OAuth Callback
- **Frontend**: `OAuthCallback.tsx` receives redirect
- **Backend**: `GET /api/v1/emails/oauth/callback`
  - Validates state token (security check)
  - Exchanges `code` for `access_token` and `refresh_token`
  - Gets user email from Google API
  - Checks for existing account (prevents duplicates)
  - Creates/updates `EmailAccount` in database
  - Encrypts tokens before storing
- **Frontend**: Auto-triggers email sync
- **Result**: Account connected, redirected to inbox

---

### 2. **Email Synchronization**

#### Manual Sync (User Clicks "Sync")
- **Frontend**: `POST /api/v1/emails/sync`
- **Backend**: `sync_emails()` function
  1. Gets all user's connected accounts
  2. For each account:
     - Decrypts OAuth tokens
     - Connects to Gmail API (via `GmailService`)
     - Fetches last 50 emails
     - For each email:
       - Extracts: subject, sender, body, date, labels
       - Checks if email already exists (by `provider_message_id`)
       - If new, creates `EmailItem` record
       - **AI Processing**:
         - Extracts dates using NLP
         - Calculates priority score
         - Extracts tasks from email content
       - Saves to database
  3. Updates `last_sync_at` timestamp
  4. Returns sync count

#### Auto Sync (After Connection)
- Triggered automatically after OAuth callback
- Same process as manual sync

---

### 3. **Email Display (Inbox View)**

#### Frontend Request
- **Component**: `EmailInbox.tsx`
- **API Call**: `GET /api/v1/emails?page=1&page_size=50`
- **Backend**: `list_emails()` function
  1. Gets user's email account IDs
  2. Queries `EmailItem` table for user's emails
  3. Orders by `received_at DESC` (newest first)
  4. Paginates results
  5. Converts UUIDs to strings for JSON response
  6. Returns: `{emails: [...], total: N, page: 1, page_size: 50}`

#### Frontend Rendering
- **Display Format** (Gmail-like):
  - **Unread Indicator**: Blue dot + colored left border
  - **Starred/Important**: Yellow star icon
  - **Sender Name**: Bold if unread
  - **Subject**: Bold if unread
  - **Preview Text**: First 100 chars of body or AI summary
  - **Date/Time**: Formatted (e.g., "Jan 25, 4:01 PM")
  - **Priority Badge**: Red badge for high priority (>70)
  - **Task Badge**: Blue badge showing task count

---

### 4. **Email Details (When Clicked)** ✅ IMPLEMENTED

#### Flow:
1. **User Clicks Email** → Navigate to `/emails/:emailId`
2. **Frontend**: `EmailDetail.tsx` component
   - Fetches: `GET /api/v1/emails/:emailId`
   - Displays full email content in Gmail-like format
3. **Backend**: `get_email()` function
   - Validates user owns the email (joins with EmailAccount)
   - Returns full email data with all AI insights
   - Converts UUID to string for response
4. **Display Features**:
   - ✅ Full sender info (name + email)
   - ✅ Complete subject with star indicator
   - ✅ Full body text/HTML rendering
   - ✅ AI Summary (if available)
   - ✅ Extracted Tasks list
   - ✅ Extracted Dates list
   - ✅ Priority score badge
   - ✅ Read/Unread status
   - ✅ Action buttons (Reply, Forward, Mark as Read)
   - ✅ Back to Inbox button

---

### 5. **AI Processing Pipeline**

#### When Email is Synced:
1. **NLP Extraction** (`nlp_extractor.py`):
   - Extracts dates from email text
   - Stores in `ai_extracted_dates` JSON field

2. **Priority Scoring** (`priority_scorer.py`):
   - Analyzes email content
   - Checks for urgent keywords
   - Considers sender importance
   - Calculates score (0-100)
   - Stores in `ai_priority_score`

3. **Task Extraction** (`task_generator.py`):
   - Uses LLM to identify actionable items
   - Extracts tasks from email body
   - Stores in `ai_extracted_tasks` JSON field
   - Can create `Task` records automatically

4. **Summary Generation** (Future):
   - Generates AI summary
   - Stores in `ai_summary` field

---

### 6. **Database Schema**

#### `email_accounts` Table:
- `id` (UUID): Primary key
- `user_id` (UUID): Foreign key to users
- `provider` (string): 'gmail', 'outlook', 'imap'
- `email_address` (string): User's email
- `access_token_encrypted` (text): Encrypted OAuth token
- `refresh_token_encrypted` (text): Encrypted refresh token
- `sync_enabled` (boolean): Auto-sync enabled?
- `last_sync_at` (datetime): Last sync timestamp

#### `email_items` Table:
- `id` (UUID): Primary key
- `email_account_id` (UUID): Foreign key to email_accounts
- `provider_message_id` (string): Unique ID from provider
- `subject` (text): Email subject
- `sender_email` (string): Sender's email
- `sender_name` (string): Sender's name
- `body_text` (text): Plain text body
- `body_html` (text): HTML body
- `received_at` (datetime): When email was received
- `is_read` (boolean): Read status
- `is_important` (boolean): Starred/important
- `ai_summary` (text): AI-generated summary
- `ai_priority_score` (integer): Priority score (0-100)
- `ai_extracted_tasks` (JSONB): Extracted tasks
- `ai_extracted_dates` (JSONB): Extracted dates

---

### 7. **Security Features**

1. **Token Encryption**:
   - OAuth tokens encrypted before storing
   - Uses `encryption.py` utilities
   - Decrypted only when needed for API calls

2. **User Isolation**:
   - All queries filtered by `user_id`
   - Users can only see their own emails
   - OAuth state includes user_id for validation

3. **Token Refresh**:
   - Automatic refresh when expired
   - Updates stored tokens
   - Handles refresh failures gracefully

---

### 8. **Error Handling**

- **OAuth Failures**: Clear error messages, retry options
- **Sync Failures**: Logged but don't break connection
- **API Failures**: Graceful degradation, user notifications
- **Duplicate Prevention**: Checks before creating accounts/emails

---

### 9. **Future Enhancements**

- [x] Email detail view (click to open) ✅ DONE
- [ ] Mark as read/unread (backend endpoint needed)
- [ ] Reply functionality
- [ ] Archive/Delete
- [ ] Search functionality
- [ ] Filters (unread, important, etc.)
- [ ] Auto-sync scheduling (Celery tasks)
- [ ] Email threading
- [ ] Attachments handling
- [ ] Rich HTML email rendering

---

## 🔄 Complete User Journey

1. **Sign Up/Login** → User authenticates
2. **Connect Gmail** → OAuth flow → Account saved
3. **Auto Sync** → Emails fetched → AI processed → Stored
4. **View Inbox** → Emails displayed in Gmail-like format
5. **Click Email** → (TODO) Open detail view
6. **Manual Sync** → User clicks "Sync" → New emails fetched
7. **Search** → Filter emails by query
8. **Tasks** → Extracted tasks appear in Tasks page

---

## 📊 Data Flow Diagram

```
User → Frontend → Backend API → Gmail API
                ↓
            Database (PostgreSQL)
                ↓
            AI Processing
                ↓
            Tasks/Dates Extraction
                ↓
            Frontend Display
```

---

This workflow ensures secure, efficient email management with AI-powered insights!
