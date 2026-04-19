import discord
import traceback
import asyncio
import aiosqlite


# =====================
# 📤 SAFE SEND MESSAGE (V2 READY)
# =====================
async def safe_send(target, content=None, embed=None, view=None, ephemeral=False):

    try:
        # =====================
        # INTERACTION
        # =====================
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

        # =====================
        # CHANNEL
        # =====================
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
        log_error("SAFE_SEND ERROR", e)


# =====================
# 📡 SAFE GET CHANNEL
# =====================
def safe_get_channel(bot, channel_id):

    try:
        if not channel_id:
            return None

        return bot.get_channel(int(channel_id))

    except Exception as e:
        log_error("GET_CHANNEL ERROR", e)
        return None


# =====================
# 🧠 SAFE DB EXECUTE (🔥 V2 FIXED)
# =====================
async def safe_db_execute(db_path, query, params=(), fetch="all"):

    try:
        async with aiosqlite.connect(db_path) as db:
            cur = await db.execute(query, params)

            if fetch == "one":
                return await cur.fetchone()

            if fetch == "all":
                return await cur.fetchall()

            await db.commit()
            return True

    except Exception as e:
        log_error("DB ERROR", e)
        return None


# =====================
# ⚠️ ERROR LOGGER
# =====================
def log_error(title, error):

    print(f"\n[ERROR] {title}")
    print("=" * 40)
    print(str(error))
    print(traceback.format_exc())
    print("=" * 40)


# =====================
# ⏱ SAFE ASYNC LOOP (PRODUCTION)
# =====================
async def safe_loop(func, delay, running_flag=None):

    while True:

        if running_flag is not None and not running_flag():
            break

        try:
            await func()

        except Exception as e:
            log_error("LOOP ERROR", e)

        await asyncio.sleep(delay)
