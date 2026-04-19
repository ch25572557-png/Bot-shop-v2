import discord
import traceback
import asyncio

# =====================
# 📤 SAFE SEND MESSAGE (IMPROVED)
# =====================
async def safe_send(target, content=None, embed=None, view=None, ephemeral=False):

    try:
        # 🔥 Interaction case
        if isinstance(target, discord.Interaction):

            if target.response.is_done():
                return await target.followup.send(
                    content=content,
                    embed=embed,
                    view=view,
                    ephemeral=ephemeral
                )

            return await target.response.send_message(
                content=content,
                embed=embed,
                view=view,
                ephemeral=ephemeral
            )

        # 🔥 Channel case
        if target:
            return await target.send(
                content=content,
                embed=embed,
                view=view
            )

    except discord.Forbidden:
        print("[SAFE_SEND] ❌ Missing permissions")
    except discord.HTTPException as e:
        print("[SAFE_SEND] ❌ HTTP error:", e)
    except Exception as e:
        print("[SAFE_SEND ERROR]", e)


# =====================
# 📡 SAFE GET CHANNEL (IMPROVED)
# =====================
def safe_get_channel(bot, channel_id):

    try:
        if not channel_id:
            return None

        channel = bot.get_channel(int(channel_id))

        if channel is None:
            print("[CHANNEL WARN] Channel not found:", channel_id)

        return channel

    except Exception as e:
        print("[GET_CHANNEL ERROR]", e)
        return None


# =====================
# 🧠 SAFE DB EXECUTE (IMPROVED)
# =====================
def safe_db_execute(conn, query, params=(), commit=False):

    try:
        cur = conn.cursor()
        cur.execute(query, params)

        result = None

        try:
            result = cur.fetchall()
        except:
            result = None

        if commit:
            conn.commit()

        return result

    except Exception as e:
        print("[DB ERROR]", e)
        return None


# =====================
# ⚠️ ERROR LOGGER (IMPROVED)
# =====================
def log_error(title, error):

    print(f"\n[ERROR] {title}")
    print("=" * 40)
    print(str(error))
    print(traceback.format_exc())
    print("=" * 40)


# =====================
# ⏱ SAFE ASYNC LOOP (IMPROVED)
# =====================
async def safe_loop(func, delay):

    while True:
        try:
            await func()

        except Exception as e:
            log_error("LOOP ERROR", e)

        await asyncio.sleep(delay)
