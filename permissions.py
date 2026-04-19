import discord

# =====================
# 👑 ADMIN CHECK
# =====================
def is_admin(bot, user: discord.Member):

    try:
        admin_role_id = bot.brain.role("ADMIN_ROLE")

        if not admin_role_id:
            return False

        return any(role.id == int(admin_role_id) for role in user.roles)

    except Exception as e:
        print("[PERMISSION ERROR] admin check:", e)
        return False


# =====================
# 🚫 BLOCK NON-ADMIN (INTERACTION)
# =====================
async def admin_only(interaction: discord.Interaction):

    if not isinstance(interaction.user, discord.Member):
        return False

    bot = interaction.client

    if is_admin(bot, interaction.user):
        return True

    await interaction.response.send_message(
        "❌ คุณไม่มีสิทธิ์ใช้ฟีเจอร์นี้",
        ephemeral=True
    )

    return False


# =====================
# 👁️ HIDE BUTTON FOR NON-ADMIN
# =====================
def hide_for_non_admin(bot, user: discord.Member):

    try:
        return is_admin(bot, user)
    except:
        return False


# =====================
# 🧠 TICKET LIMIT CHECK (1 ACTIVE ONLY)
# =====================
def can_open_ticket(bot, user_id):

    try:
        cur = bot.mem.conn.cursor()

        cur.execute(
            "SELECT COUNT(*) FROM tickets WHERE user_id=? AND status='open'",
            (user_id,)
        )

        count = cur.fetchone()[0]

        return count == 0

    except Exception as e:
        print("[PERMISSION ERROR] ticket check:", e)
        return False


# =====================
# 🔒 GUARD WRAPPER (DECORATOR STYLE)
# =====================
async def require_admin(interaction: discord.Interaction):

    if not isinstance(interaction.user, discord.Member):
        return False

    if is_admin(interaction.client, interaction.user):
        return True

    await interaction.response.send_message(
        "❌ Admin only",
        ephemeral=True
    )

    return False
