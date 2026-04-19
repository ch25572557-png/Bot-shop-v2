import discord


# =====================
# 👑 ADMIN CHECK (FIXED)
# =====================
def is_admin(bot, user: discord.Member):

    try:
        # ✅ รองรับ admin permission จริง
        if user.guild_permissions.administrator:
            return True

        role_id = bot.brain.role("ADMIN_ROLE")

        if not role_id:
            return False

        return any(r.id == role_id for r in user.roles)

    except Exception as e:
        print("[PERMISSION ERROR]", e)
        return False


# =====================
# 🚫 ADMIN ONLY GUARD
# =====================
async def admin_only(interaction: discord.Interaction):

    if not isinstance(interaction.user, discord.Member):
        return False

    if is_admin(interaction.client, interaction.user):
        return True

    if not interaction.response.is_done():
        await interaction.response.send_message(
            "❌ คุณไม่มีสิทธิ์ใช้ฟีเจอร์นี้",
            ephemeral=True
        )

    return False


# =====================
# 🔒 SHORT ALIAS
# =====================
async def require_admin(interaction: discord.Interaction):
    return await admin_only(interaction)


# =====================
# 👁️ VIEW VISIBILITY
# =====================
def hide_for_non_admin(bot, user: discord.Member):

    try:
        return is_admin(bot, user)
    except:
        return False


# =====================
# 🎫 TICKET LIMIT (FIXED REAL)
# =====================
def can_open_ticket(bot, user_id):

    try:
        cur = bot.mem.conn.cursor()

        # 🔥 FIX: join orders เพื่อหา user
        cur.execute("""
            SELECT COUNT(*)
            FROM tickets t
            JOIN orders o ON t.order_id = o.id
            WHERE o.user = ?
            AND o.status != 'DONE'
            AND o.status != 'CANCELLED'
        """, (str(user_id),))

        count = cur.fetchone()[0]

        return count == 0

    except Exception as e:
        print("[PERMISSION ERROR] ticket check:", e)
        return False
