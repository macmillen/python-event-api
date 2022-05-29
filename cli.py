import click
import requests

ENDPOINT = "http://127.0.0.1:5000"


@click.command()
def cli():
    click.secho("\nWelcome to the ticket store\n", fg='yellow')

    events = requests.get(f"{ENDPOINT}/events").json()["events"]

    click.secho("EVENTS:", fg='bright_blue')
    click.echo("ID\tName")
    for event in events:
        click.echo(f"{event['id']}\t{event['name']}")

    click.echo("\nWhich event do you want to purchase tickets for?")
    event_id = click.prompt("Please enter an event ID", type=int)

    products = requests.get(f"{ENDPOINT}/products/{event_id}").json()["products"]

    click.secho("\nPRODUCTS:", fg='bright_blue')
    click.echo("ID\tName")
    for product in products:
        click.echo(f"{product['id']}\t{product['name']}")

    product_list = []

    while(True):
        product_id = click.prompt("Enter Product ID", type=int)
        quantity = click.prompt("Enter Quantity", type=int)
        product_list.append({"id": product_id, "quantity": quantity})
        if click.confirm('Do you want to add more products to the cart?', default=True) == False:
            break

    click.echo("\nID\tQuantity")

    for product in product_list:
        click.echo(f"{product['id']}\t{product['quantity']}")

    receipt = requests.get(f"{ENDPOINT}/total_service_fee/{event_id}", json={"products": product_list}).text
    click.echo(receipt)


if __name__ == '__main__':
    cli()
