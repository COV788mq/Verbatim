import discord
import json
from verbatim.otherThings import get_file, save_file

settings = get_file('settings.json')
TOKEN = settings["discord token"]

client = discord.Client()

COMMAND_DESCRIPTIONS = [
    ('register', ("Registers you to Verbatim's 'database' of sorts. "
                 "It makes things faster I guess, and makes it so different users can have the same path name.")),
    ('createpath `path name`', "Creates your first path and automatically assigns the hub to your current channel."),
    ('sethub `path name`', ("Assigns a hub for your path, this is where you do all your publishing, "
                           "it helps optimize things and prevents cluttering")),
    ('addbranch `path name`', ("Adds a branch to a path, this way you can publish in the hub and all "
                              "those messages will be passed down to the branches")),
    ('publish `path name` `content`', ("Publishes your messages in a typical text form through a branch "
                                      "of your choice\n(Remember to do this in your path's hub, also you "
                                      "can't ping roles because Discord API)")),
    ('viewpaths', "View your currently registered paths, including branches"),
    ('removepath `path name`', "Deletes a path, note, there is no confirmation, so you do it once, and it's gone"),
    ('removebranch `path name` `channel ID`', "Deletes a branch, no confirmation, get channel ID with -viewpaths"),
    ('faq', ("Few some questions and answers (they aren't really 'frequently' "
            "asked because as of now the bot isn't popular enough :/)")),
]


async def print_help(summon: str, channel) -> None:
    embed_help = discord.Embed(
        title="Help",
        description="A quick how 2 on how to do things",
        color=discord.Color.dark_orange(),
    )
    for command, description in COMMAND_DESCRIPTIONS:
        embed_help.add_field(name=f'{summon}{command}', value=description, inline=False)
    await channel.send(embed=embed_help)


@client.event
async def on_ready():
    print('lets get this party started')


@client.event
async def on_message(message):
    # role check
    if message.author.bot:
        return

    ''' if message.author.top_role.permissions.manage_guild == False:
        return '''

    # check for summon
    summon = '-'
    summons = get_file('summons.json')
    if str(message.guild.id) in summons:
        summon = summons[str(message.guild.id)]
    the_message = message.content.lower().split(' ')
    header = the_message[0].lower()
    channel = message.channel

    # it's the help page u maga 4head
    if header == f'{summon}help':
        await print_help(summon=summon, channel=channel)

    # registers a user to the bot
    elif header == f'{summon}register':
        path_file = get_file('../../pathfile.json')
        is_user = False
        for user in path_file:
            if user == str(message.author.id):
                is_user = True
        if is_user:
            await channel.send("you've already registered!")
            return
        path_file[message.author.id] = {
            "paths": {}
        }
        await channel.send(f'Registered {message.author}')
        save_file(path_file, '../../pathfile.json')

    # creates a path
    if header == f'{summon}createpath':

        string_id = str(message.author.id)

        # prelim checks
        if isinstance(message.channel, discord.DMChannel):
            await channel.send("You can't set a path in a DM")
            return
        if len(the_message) > 2 or len(the_message) < 2:
            await channel.send("Path names have to be one string, no spaces")
            return
        path_file = get_file('../../pathfile.json')

        if string_id not in path_file:
            await channel.send("You have to -register first before creating a path")

        user_paths = path_file[string_id]["paths"]

        if user_paths != 0:
            for path in user_paths:
                if path == the_message[1]:
                    await channel.send(f"You already have a path by the name of {the_message[1]}")
                    return

        user_paths[the_message[1]] = {
            "pathserver": message.channel.guild.id,
            "pathbranches": [
            ]
        }
        await channel.send(f'Path created with name `{the_message[1]}`')
        save_file(path_file, 'pathfile.json')

    # adds a branch
    if header == f'{summon}addbranch':

        path_file = get_file('../../pathfile.json')
        path_name = the_message[1]
        string_id = str(message.author.id)

        # prelim checks
        if isinstance(message.channel, discord.DMChannel):
            await channel.send("Do this in a server")
            return
        if len(the_message) > 2:
            await channel.send("Path names have to be one 'word', with no spaces")
            return

        if string_id not in path_file:
            await channel.send("You must first register before creating your path... before then, assigning a hub...")
            return

        user_paths = path_file[string_id]["paths"]

        if len(user_paths) == 0 or path_name not in user_paths:
            await channel.send("You can't add a branch to a path that doesn't exist!")
            return

        branches = user_paths[path_name]["pathbranches"]
        if message.channel.id in branches:
            await channel.send("You've already added this channel!")
            return
        branches.append(message.channel.id)

        save_file(path_file, '../../pathfile.json')
        await channel.send(f'Successfully added `#{message.channel.name}` to path `{path_name}`')

    # views paths
    if header == f'{summon}viewpaths':

        path_file = get_file('../../pathfile.json')
        string_id = str(message.author.id)

        # checks
        if string_id not in path_file:
            await channel.send("You have to register first, and then create a path")
            return

        if len(path_file[string_id]["paths"]) == 0:
            await channel.send("You don't have any paths!")
            return

        if message.author.dm_channel is None:
            await message.author.create_dm()
        dm_channel = message.author.dm_channel
        await dm_channel.send("Your paths here")
        for pathname in path_file[string_id]["paths"]:
            path = path_file[string_id]["paths"][pathname]
            embed_path = discord.Embed(title=f'Path: {pathname}', color=discord.Color.dark_orange())
            branches = ""
            if not path["pathbranches"]:
                embed_path.add_field(name="Branches", value="You have to first set a branch!", inline=False)
            else:
                for branch in path["pathbranches"]:
                    branchchannel = client.get_channel(branch)
                    branches += (f"\t`#{branchchannel.name}` in server `{branchchannel.guild.name}`"
                                 f"\n\tChannel ID: `{branch}`\n")
                embed_path.add_field(name="Branches", value=branches, inline=False)
            await dm_channel.send(embed=embed_path)
        await channel.send("Check your DM's")

    # publishes a message
    if header == f'{summon}publish':

        path_name = the_message[1]
        path_file = get_file('../../pathfile.json')
        string_user_id = str(message.author.id)

        # checks
        if string_user_id not in path_file:
            await channel.send("You have to register, create a path, and add branches before publishing a message")
            return

        if len(path_file[string_user_id]["paths"]) == 0:
            await channel.send("You haven't created any paths yet, how are you gonna send again? :think:")
            return

        if path_name not in path_file[string_user_id]["paths"]:
            await channel.send(f"You haven't created a path under the name `{path_name}` yet")
            return

        if len(path_file[string_user_id]["paths"][path_name]["pathbranches"]) == 0:
            await channel.send("You haven't added any branches to this path first, do that and then publish a message")
            return

        if len(the_message) < 3:
            await channel.send("Your message actually needs to have content")
            return

        for branch in path_file[string_user_id]["paths"][path_name]["pathbranches"]:
            content = ''
            if len(the_message) > 3:
                content = ' '.join(the_message[2:])
            elif len(the_message) == 3:
                content = the_message[2]
            channel2send2 = client.get_channel(branch)
            await channel2send2.send(content)

    # deletes a path
    if header == f'{summon}removepath':

        if len(the_message) < 2:
            await channel.send("You have to specificy a path to delete!")
            return

        path_file = get_file('../../pathfile.json')
        string_id = str(message.author.id)
        path_name = the_message[1]
        user_paths = path_file[string_id]["paths"]

        if string_id not in path_file:
            await channel.send("You have to register first!")
            return

        if user_paths == {}:
            await channel.send("You have to first have a path before you can remove one")
            return

        if path_name not in user_paths:
            await channel.send(
                f"You don't have a path under the name of `{path_name}`, use `-viewpaths` to view your created paths",
            )
            return

        del (path_file[string_id]["paths"][path_name])
        await channel.send("lol ok")
        await channel.send(f"Deleted path `{path_name}`")
        save_file(path_file, '../../pathfile.json')

    # deletes a branch from a path
    if header == f'{summon}removebranch':
        if len(the_message) < 3:
            await channel.send("You're missing some variables there")
            return
        elif len(the_message) > 3:
            await channel.send("Uh, you might think this bot excepts a lot of variables... there's 3, actually")
            return

        path_file = get_file('../../pathfile.json')
        string_id = str(message.author.id)
        path_name = the_message[1]
        path_branch = int(the_message[2])
        paths = path_file[string_id]["paths"]

        if string_id not in path_file:
            await channel.send("You have to first register!")
            return

        if paths == {}:
            await channel.send("You have to first have a path, and then branches on that path...")
            return

        if path_name not in paths:
            await channel.send(
                f"You don't have a path under the name of `{path_name}`, use `-viewpaths` to view your created paths"
            )
            return

        if not paths[path_name]["pathbranches"]:
            await channel.send("Your path first has to have branches before I can remove them ")
            return

        if path_branch not in paths[path_name]["pathbranches"]:
            await channel.send(
                f"So like, `{client.get_channel(path_branch).name}`'s not, that's not a branch you have "
                f"installed on your path (pro tip: use -viewpaths)",
            )
            return

        paths[path_name]["pathbranches"].remove(path_branch)
        await channel.send(
            f"Sucessfully deleted branch `#{client.get_channel(path_branch).name}` from path `{path_name}`"
        )
        save_file(path_file, '../../pathfile.json')

    # changes the summon for a thing
    if header == f'{summon}summon':
        if len(the_message) != 2:
            await channel.send("Summons have to be 1 string only, with no spaces")

        else:
            str_guild = str(message.guild.id)
            summons = get_file('summons.json')
            summons[str_guild] = the_message[1]
            save_file(summons, 'summons.json')
            await channel.send(f'Changed the summon for Verbatim in server {message.guild.name} to {the_message[1]}')

    # faq
    if header == f'{summon}faq':
        embedFaq = discord.Embed(title="FAQ", description="Frequently asked questions that aren't frequently asked")
        embedFaq.add_field(name="Can it function where it just automatically publishes a message from a channel?",
                           value="Kinda, originally it could do that, but the idea was scrapped in favor for a {summon}publish anywhere approach",
                           inline=False)
        await channel.send(embed=embedFaq)


client.run(TOKEN)
