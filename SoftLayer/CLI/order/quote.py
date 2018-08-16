"""Save an order as quote"""
# :license: MIT, see LICENSE for more details.

import json

import click

from SoftLayer.CLI import environment
from SoftLayer.CLI import exceptions
from SoftLayer.CLI import formatting
from SoftLayer.managers import ordering

COLUMNS = ['keyName',
           'description',
           'cost', ]

@click.command()
@click.argument('package_keyname')
@click.argument('location')
@click.option('--preset',
              help="The order preset (if required by the package)")
@click.option('--name',
              help="Quote name (optional)")
@click.option('--send-email',
              is_flag=True,
              help="Quote will be sent to the email address")
@click.option('--complex-type', help=("The complex type of the order. This typically begins"
                                      " with 'SoftLayer_Container_Product_Order_'."))
@click.option('--extras',
              help="JSON string denoting extra data that needs to be sent with the order")
@click.argument('order_items', nargs=-1)
@environment.pass_env
def cli(env, package_keyname, location, preset, name, email, complex_type,
        extras, order_items):
    """Save an order as quote.

    This CLI command is used for saving an order in quote of the specified package in
    the given location (denoted by a datacenter's long name). Orders made via the CLI
    can then be converted to be made programmatically by calling
    SoftLayer.OrderingManager.place_order() with the same keynames.

    Packages for ordering can be retrieved from `slcli order package-list`
    Presets for ordering can be retrieved from `slcli order preset-list` (not all packages
    have presets)

    Items can be retrieved from `slcli order item-list`. In order to find required
    items for the order, use `slcli order category-list`, and then provide the
    --category option for each category code in `slcli order item-list`.

    \b
    Example:
        # Order an hourly VSI with 4 CPU, 16 GB RAM, 100 GB SAN disk,
        # Ubuntu 16.04, and 1 Gbps public & private uplink in dal13
        slcli order quote --name " My quote name" --email CLOUD_SERVER DALLAS13 \\
            GUEST_CORES_4 \\
            RAM_16_GB \\
            REBOOT_REMOTE_CONSOLE \\
            1_GBPS_PUBLIC_PRIVATE_NETWORK_UPLINKS \\
            BANDWIDTH_0_GB_2 \\
            1_IP_ADDRESS \\
            GUEST_DISK_100_GB_SAN \\
            OS_UBUNTU_16_04_LTS_XENIAL_XERUS_MINIMAL_64_BIT_FOR_VSI \\
            MONITORING_HOST_PING \\
            NOTIFICATION_EMAIL_AND_TICKET \\
            AUTOMATED_NOTIFICATION \\
            UNLIMITED_SSL_VPN_USERS_1_PPTP_VPN_USER_PER_ACCOUNT \\
            NESSUS_VULNERABILITY_ASSESSMENT_REPORTING \\
            --extras '{"virtualGuests": [{"hostname": "test", "domain": "softlayer.com"}]}' \\
            --complex-type SoftLayer_Container_Product_Order_Virtual_Guest

    """
    manager = ordering.OrderingManager(env.client)

    if extras:
        extras = json.loads(extras)

    args = (package_keyname, location, order_items)
    kwargs = {'preset_keyname': preset,
              'extras': extras,
              'quantity': 1,
              'quoteName': name,
              'sendQuoteEmailFlag': email,
              'complex_type': complex_type}

    order = manager.save_quote(*args, **kwargs)

    table = formatting.KeyValueTable(['name', 'value'])
    table.align['name'] = 'r'
    table.align['value'] = 'l'
    table.add_row(['id', order['orderId']])
    table.add_row(['created', order['orderDate']])
    table.add_row(['status', order['placedOrder']['status']])
    env.fout(table)