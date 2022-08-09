import itertools
import json
import discord
from discord import app_commands
from pbinfo import pbinfo
from util import dsutil

pb=json.load(open('pbinfo/_pb.json'))

async def problema_autocomplete(interaction: discord.Interaction, current: str):
  auto = (app_commands.Choice(name=f'#{v} {k}', value=v) for k,v in pb.items() if current.lower() in f'#{v} {k.lower()}')
  return list(itertools.islice(auto, 10)) # autocomplete up to 10 items

class PbinfoGroup(app_commands.Group):
  def __init__(self):
    super().__init__(name='pbinfo', description='Comenzi legate de pbinfo')

  @app_commands.command(name='problema', description='Caută o problemă pe pbinfo')
  @app_commands.describe(id='Numele problemei')
  @app_commands.autocomplete(id=problema_autocomplete)
  async def problema(self, interaction: discord.Interaction, id: int):
    await interaction.response.defer()
    
    data = await pbinfo.get_problem(id)
    if data['error']:
      if data['error'] == 404:
        embed = dsutil.create_error_embed('Problema nu există.')
      else:
        embed = dsutil.create_error_embed('Cauza este necunoscută.')
      await interaction.edit_original_response(embed=embed)
      return

    embed = discord.Embed(title=f'Problema #{id} {data["name"]} - {data["solutions"]} Soluții', description=f'{data["categories"]}', colour=dsutil.LIGHT_BLUE)
    dsutil.add_data(embed, 'Enunț', value=data['statement'])
    dsutil.add_data(embed, name='Cerința', value=data['task'])
    dsutil.add_data(embed, name='Date de intrare', value=data['input'])
    dsutil.add_data(embed, name='Date de ieșire', value=data['output'])
    dsutil.add_data(embed, name='Exemplu', value=data['example'])
    if data['file_in']:
      dsutil.add_data(embed, name='Exemplu', value=f'{data["file_in"]}\n```{data["in_example"]}```\n{data["file_out"]}\n```{data["out_example"]}```')
    if data['author']:
      embed.set_footer(text=f'Postată de {data["author"][0]}', icon_url=data['author'][1])

    # Link to problem button
    btn = discord.ui.Button(style=discord.ButtonStyle.link, url=f'https://www.pbinfo.ro/probleme/{id}', label='Problema')
    view = discord.ui.View().add_item(btn)
    await interaction.edit_original_response(embed=embed, view=view)
  
  @app_commands.command(name='cont', description='Vezi contul de pbinfo al unui utilizator')
  @app_commands.describe(nume='Numele utilizatorului')
  async def cont(self, interaction: discord.Interaction, nume: str):
    await interaction.response.defer()
    
    data = await pbinfo.get_account(nume)
    if data['error']:
      if data['error'] == 404:
        embed = dsutil.create_error_embed('Utilizatorul nu există.')
      elif data['error'] == 403:
        embed = dsutil.create_error_embed('Utilizatorul are contul privat.')
      else:
        embed = dsutil.create_error_embed('Cauza este necunoscută.')
      await interaction.edit_original_response(embed=embed)
      return
    
    problems = pbinfo.process_problems(data['problems'])
    embed = dsutil.create_embed(nume, f':white_check_mark: {len(problems["total_solved"])} Probleme rezolvate\n:no_entry: {len(problems["total_tried"])} Probleme încercate dar nerezolvate\n:triangular_flag_on_post: {problems["total"]} Surse trimise\n:checkered_flag: {data["success"]}% Success', [], colour=dsutil.LIGHT_BLUE)
    for cls in range(9, 12):
      embed.add_field(name=f'Clasa a {cls}-a', value=f'{len(problems["solved"][f"{cls}"])} Probleme rezolvate - {len(problems["tried"][f"{cls}"])} Probleme nerezolvate', inline=False)
    embed.set_author(name=data['display_name'], url=f'https://www.pbinfo.ro/profil/{nume}', icon_url=data['avatar'])
    embed.set_thumbnail(url=data['goal'])

    # Link to account button
    btn = discord.ui.Button(style=discord.ButtonStyle.link, url=f'https://www.pbinfo.ro/profil/{nume}', label='Cont')
    view = discord.ui.View().add_item(btn)
    await interaction.edit_original_response(view=view, embed=embed)
