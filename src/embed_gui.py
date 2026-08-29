import discord
from discord.ext import commands


class EmbedGui(discord.ui.View):
    def __init__(self, honeypots: list[dict], ctx: commands.Context):
        super().__init__(timeout=180)  # Times out after 3 minutes
        self.honeypots = honeypots
        self.ctx = ctx
        self.author_id = ctx.author.id
        self.current_page = 0
        self.max_pages = len(honeypots)
        self.update_buttons()

    def create_embed(self) -> discord.Embed:
        data = self.honeypots[self.current_page]

        embed = discord.Embed(
            title="Honeypot Details",
            description=f"**Channel:** {self.ctx.guild.get_channel(data['channel']).jump_url}"
                        f"\n**Punishment:** {data['type']}"
                        f"\n**Duration:** {data['duration']} hours",
            color=0xd8a31e
        )

        embed.set_footer(text=f"Page {self.current_page + 1} of {self.max_pages}")
        return embed

    def update_buttons(self):
        # Disable/enable navigation buttons based on current position
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page == self.max_pages - 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Prevent users other than the command invoker from using the buttons
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("You cannot control this menu.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        self.update_buttons()
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    async def on_timeout(self):
        # Gray out buttons when the menu times out
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True