import discord

from verbatim.otherThings import get_file, save_file

settings = get_file("settings.json")
TOKEN = settings["NzI5Nzc0OTM1NzkwMzIxNzM0.XwOkNQ.CPy6LTB6ELFzgwWcqT2lpsIPGVk"]
embed_color = 16604755


client = discord.Client()

COMMAND_DESCRIPTIONS = [
    ("path add/remove `path name`", ("Add and removes Paths tied to your server")),
    (
        "branch add/remove `server ID` `path name`",
        (
            "Add or remove Paths on your server. This is required to start adding branches."
        ),
    ),
    (
        "publish `path name` `content`",
        (
            "Publishes your message to all Branches tied to the specified Path. It can ping @here, @everyone, and individual Users, but not Server-Roles and Server-Channels."
        ),
    ),
    ("viewpaths", ("Grabs a list of Paths+Branches on your server")),
    (
        "serverid",
        (
            "Gets the current server's id, this is useful for adding and removing Branches (see above)"
        ),
    ),
    (
        "whitelist",
        (
            "Add or remove a non-Admin user from being able to use the -publish and -viewpaths command"
        ),
    ),
    (
        "Prefix or `@verbatim prefix`",
        (
            "Changes prefixd from `-` to whatever you'd like it to be. (i.e. `!` or `v?`)"
        ),
    ),
    ("ping", ("Gets and returns your latency")),
]

WHITELIST_HELP = [
    (
        "whitelist add `@user`",
        (
            "Adds a user to the whitelist. Whitelisted users can access `publish` and `viewpaths` commands only"
        ),
    ),
    ("whitelist remove `@user`", ("Removes a user from the whitelist.")),
    ("whitelist view", ("Lists currently whitelisted users in the server.")),
]

PATH_HELP = [
    (
        "path add `pathname`",
        ("Creates a Path with a unique name to the current server"),
    ),
    (
        "path remove `pathname`",
        ("Removes a Path from the server, note there is no confirmation"),
    ),
]


class Error(Exception):
    def __init__(self, err_msg):
        self.err_msg = err_msg


async def print_help(type_help: str, summon: str, channel) -> None:
    if type_help == "help":
        embed_help = discord.Embed(
            title="Help",
            description="How to do the things that do the things",
            color=discord.Colour(embed_color),
        )
        for command, description in COMMAND_DESCRIPTIONS:
            embed_help.add_field(
                name=f"{summon}{command}", value=description, inline=False
            )
    elif type_help == "path_help":
        embed_help = discord.Embed(
            title="Path Help",
            description="How to create and delete paths",
            color=discord.Color(embed_color),
        )
        for command, description in PATH_HELP:
            embed_help.add_field(
                name=f"{summon}{command}", value=description, inline=False
            )
    elif type_help == "whitelist_help":
        embed_help = discord.Embed(
            title="Whitelist Help",
            description="How to add, remove people and view the whitelist",
            color=discord.Color(embed_color),
        )
        for command, description in WHITELIST_HELP:
            embed_help.add_field(
                name=f"{summon}{command}", value=description, inline=False
            )

    await channel.send(embed=embed_help)



@client.event
async def on_ready():
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="Branching out | -help"),
    )
    print("Ready to start b r a n c h i n g out, haha get it?")


@client.event
async def on_message(message):

    # ===
    # bot check

    if message.author.bot:
        return

    # check for summon
    summon = "-"
    summons = get_file("summons.json")
    if str(message.guild.id) in summons:
        summon = summons[str(message.guild.id)]
    the_message = message.content.split(" ")
    header = the_message[0].lower()
    alt_header = ' '.join(the_message[0:2])
    channel = message.channel


    #stuff for everyone
    if "697650736498081885" in message.content and "help" in message.content:
        # it's the help page u maga 4head`
        await print_help(type_help="help", summon=summon, channel=channel)
        

    # -------------------------------------------------------------------------------------------------------------
    # stuff reserved for whitelisted people or admins
    white_list = get_file("whitelist.json")
    string_server_id = str(message.guild.id)
    if message.author.top_role.permissions.manage_guild == False and message.author.top_role.permissions.administrator == False:
        if string_server_id not in white_list:
            return
        else:
            if str(message.author.id) not in white_list[string_server_id]:
                return

    # publishes a message
    if header == f"{summon}publish":

        path_name = the_message[1]
        path_file = get_file("pathfile.json")
        string_server_id = str(message.guild.id)

        # -----------------------------
        # checks

        if string_server_id not in path_file:
            await channel.send(
                "You have to register, create a path, and add branches before publishing a message"
            )
            return

        if path_file[string_server_id] == {}:
            await channel.send("You haven't created any paths in this server :think:")
            return

        if isinstance(message.channel, discord.DMChannel):
            await channel.send("Do this in a server")
            return

        if path_name not in path_file[string_server_id]:
            await channel.send(
                f"You haven't created a path under the name `{path_name}` yet"
            )
            return

        if len(path_file[string_server_id][path_name]) == 0:
            await channel.send(
                "You haven't added any branches to this path first, do that and then publish a message"
            )
            return

        if len(the_message) < 2:
            await channel.send("Your message actually needs to have content")
            return
        # -----------------------------

        for branch in path_file[string_server_id][path_name]:
            if len(the_message) > 3:
                content = " ".join(the_message[2:])
            elif len(the_message) == 3:
                content = the_message[2]
            channel2send2 = client.get_channel(branch)
            await channel2send2.send(content)

    # views paths
    if header == f"{summon}viewpaths":

        path_file = get_file("pathfile.json")
        string_server_id = str(message.guild.id)

        # -----------------------------
        # checks

        if string_server_id not in path_file:
            await channel.send("You haven't created any paths in this server yet!")
            return

        server_paths = path_file[string_server_id]
        if server_paths == {}:
            await channel.send("There are no paths assigned to this server!")
            return

        if message.author.dm_channel == None:
            await message.author.create_dm()
        dmChannel = message.author.dm_channel

        await dmChannel.send(f"Paths assigned to server `{message.guild.name}`")
        for path in server_paths:
            """ embedPath = discord.Embed(
                title=f"Path: {path}", color=discord.Color.dark_orange()
            ) """
            branches = f"```\nPath: {path}\n-------\n"
            if server_paths[path] == []:
                branches += "No branches added"
            else:
                for branch in server_paths[path]:
                    branchchannel = client.get_channel(branch)
                    if len(branches+f"#{branchchannel.name} in server {branchchannel.guild.name}\n") > 2000:
                        await dmChannel.send(branches)
                        branches = ""
                    branches += f"#{branchchannel.name} in server {branchchannel.guild.name}\n"
            branches += "```"
            await dmChannel.send(branches)

    # server id
    if header == f"{summon}serverid":
        await channel.send(f"Your server id is `{message.guild.id}`")

    # channel id
    if header == f"{summon}channel.id":
        await channel.send(f"This channel's id is `{message.channel.id}`")

    # help
    try:
        # it's the help page u maga 4head`
        if header == f"{summon}help":
            await print_help(type_help="help", summon=summon, channel=channel)

    except Error as e:
        await channel.send(e.err_msg)
        return

    # -------------------------------------------------------------------------------------------------------------
    # stuff reserved for admins

    if message.author.top_role.permissions.administrator == False and message.author.top_role.permissions.manage_guild == False:
        return

    # path create/remove
    if header == f"{summon}path":

        # checks
        if isinstance(message.channel, discord.DMChannel):
            await channel.send(
                "You can't set a path in a DM, you have to set it in the hub"
            )
            return

        try:
            path_command = the_message[1]
        except IndexError:
            the_message.append("help")
        path_command = the_message[1]

        # checks end
        if path_command == "add" or path_command == "remove":
            if len(the_message) > 3 or len(the_message) < 3:
                await channel.send(
                    f"You either have too many variables or too little variables, use {summon}path help to view proper usage."
                )
                return
            if len(the_message[2]) > 1900: 
                await channel.send(
                    "That name is way too long, keep it short"
                )
                return
            path_name = the_message[2]
            path_file = get_file("pathfile.json")
            string_server_id = str(message.guild.id)
        else:
            await print_help(type_help="path_help", summon=summon, channel=channel)
            return

        # path add
        if path_command == "add":
            try:
                path_file[string_server_id]
            except KeyError:
                path_file[string_server_id] = {}

            server_paths = path_file[string_server_id]

            if path_name in server_paths:
                await channel.send(
                    f"You've already added a path to this server by the name {path_name}"
                )
                return
            else:
                server_paths[path_name] = []
                await channel.send(f"Path added with name `{path_name}`")
                save_file(path_file, "pathfile.json")

        # path remove
        elif path_command == "remove":
            if string_server_id not in path_file:
                await channel.send("You have to create a path first!")

            if path_name not in path_file[string_server_id]:
                await channel.send(
                    f"You don't have a path under the name of `{path_name}`, use `-viewpaths` to view your created paths"
                )
                return
            # -----------------------------

            del path_file[string_server_id][path_name]
            await channel.send("lol ok")
            await channel.send(f"Deleted path `{path_name}`")
            save_file(path_file, "pathfile.json")

    # adds a branch
    if header == f"{summon}branch":

        # -----------------------------
        # prelim checks
        if isinstance(message.channel, discord.DMChannel):
            await channel.send("Do this in a server")
            return
        if len(the_message) > 4:
            await channel.send("Path names have to be one 'word', with no spaces")
            return
        try:
            int(the_message[2])
        except ValueError:
            await channel.send(
                "Your server ID must be a string of numbers with no spaces"
            )
            return
        # -----------------------------

        path_file = get_file("pathfile.json")
        path_name = the_message[3]
        server_id = the_message[2]

        branch_command = the_message[1]

        if str(server_id) not in path_file:
            await channel.send(
                f"We've encountered an error,  you haven't created a path in your server yet!"
            )
            return
        elif path_name not in path_file[server_id]:
            await channel.send(
                f"There isn't a path by the name {path_name} registered to your server!"
            )
            return
        server_paths = path_file[server_id]
        branches = path_file[server_id][path_name]

        # branch add
        if branch_command == "add":
            if message.channel.id in branches:
                await channel.send("You've already added this channel!")
                return
            branches.append(message.channel.id)
            await channel.send(
                f"Successfully added `#{message.channel.name}` to path `{path_name}`"
            )

        # branch remove
        elif branch_command == "remove":
            if message.channel.id not in branches:
                await channel.send("You haven't added this channel yet!")
                return
            branches.remove(message.channel.id)
            await channel.send(
                f"Successfully remove `#{message.channel.name}` from path `{path_name}`"
            )

        save_file(path_file, "pathfile.json")

    # changes the summon for a thing
    if header == f"{summon}prefix" or alt_header == "<@!697650736498081885> prefix":
        if len(the_message) > 3:
            await channel.send("Summons have to be 1 string only, with no spaces")
            return

        
        strGuild = str(message.guild.id)
        summons = get_file("summons.json")
        if header == f"{summon}prefix":
            summons[strGuild] = the_message[1]
            await channel.send(
            f"Changed the summon for Verbatim in server {message.guild.name} to {the_message[1]}"
            )
        if alt_header == "<@!697650736498081885> prefix":
            summons[strGuild] = the_message[2]
            await channel.send(
            f"Changed the summon for Verbatim in server {message.guild.name} to {the_message[2]}"
            )
        save_file(summons, "summons.json")
        

    # ping
    if header == f"{summon}ping":
        embedPing = discord.Embed(
            title="Ping!",
            description=f"Ping! {round(client.latency, 2)} ms",
            color=discord.Colour(embed_color),
        )
        await channel.send(embed=embedPing)

    # -------------------------------------------------------------------------------------------------------------
    # new stuff/admin stuff
    if header == f"{summon}whitelist":

        str_guild = str(message.guild.id)
        whitelist_command = ""

        if len(the_message) == 1:
            whitelist_command = "help"
        else:
            whitelist_command = the_message[1]

        # ---------------------------------

        if whitelist_command == "add" or whitelist_command == "remove":

            white_list = get_file("whitelist.json")

            # checks
            users = message.mentions

            if len(users) == 0:
                await channel.send("You have to specify a user to whitelist")
                return

            # add
            if whitelist_command == "add":
                for userobj in users:
                    user_id = userobj.id
                    user_name = userobj.name
                    if str_guild not in white_list:
                        white_list[str_guild] = {}
                    elif user_id in white_list[str_guild]:
                        await channel.send("You've already added this user")
                        return
                    else:
                        white_list[str_guild][user_id] = user_name
                    await channel.send(
                        f"Added `{user_name}` to the whitelist for `{message.guild.name}`, they can now use {summon}publish"
                    )
                save_file(white_list, "whitelist.json")

            # remove
            elif whitelist_command == "remove":
                for userobj in users:
                    user_id = userobj.id
                    user_name = userobj.name
                    if str_guild not in white_list or white_list[str_guild] == {}:
                        await channel.send(
                            "You haven't added anyone to the whitelist yet!"
                        )
                        return
                    else:
                        del white_list[str_guild][str(user_id)]
                        await channel.send(f"Removed `{user_name}` from the whitelist")
                save_file(white_list, "whitelist.json")

        elif whitelist_command == "view":

            white_list = get_file("whitelist.json")

            # checks
            if str_guild not in white_list or white_list[str_guild] == {}:
                await channel.send(
                    f"You haven't added anyone to the whitelist yet! Use `{summon}whitelist @user` to whitelist a user"
                )
                return
            # ---

            embed_white_list = discord.Embed(title=f"{message.guild.name} Whitelist")
            embed_white_list.set_author(
                name=message.author.name, icon_url="https://i.imgur.com/6ZuCZT5.png"
            )
            embed_this = ""
            for user_id, user in white_list[str_guild].items():
                embed_this += f"{user}\n"
            embed_white_list.add_field(name="Users", value=embed_this, inline=False)

            await channel.send(embed=embed_white_list)

        elif whitelist_command == "help":
            await print_help(type_help="whitelist_help", summon=summon, channel=channel)


client.run(TOKEN)
