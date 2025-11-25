from check_compliance import check_regulatory_compliance
from product_performance import get_product_performance


def get_named_parameter(event, name):
    if name not in event:
        return None
    return event.get(name)


def lambda_handler(event, context):
    print(f"Event: {event}")
    print(f"Context: {context}")

    extended_tool_name = context.client_context.custom["bedrockAgentCoreToolName"]
    resource = extended_tool_name.split("___")[1]

    print(f"Tool requested: {resource}")

    if resource == "check_regulatory_compliance":
        product_type = get_named_parameter(event=event, name="product_type")
        region = get_named_parameter(event=event, name="region")

        if not product_type or not region:
            return {
                "statusCode": 400,
                "body": "❌ Please provide product_type and region",
            }

        try:
            compliance_status = check_regulatory_compliance(
                product_type=product_type, region=region
            )
        except Exception as e:
            print(e)
            return {
                "statusCode": 400,
                "body": f"❌ {e}",
            }

        return {
            "statusCode": 200,
            "body": compliance_status,
        }

    elif resource == "get_product_performance":
        product_id = get_named_parameter(event=event, name="product_id")
        include_vision = get_named_parameter(event=event, name="include_vision") or False

        if not product_id:
            return {
                "statusCode": 400,
                "body": "❌ Please provide product_id",
            }

        try:
            performance_data = get_product_performance(
                product_id=product_id, include_vision=include_vision
            )
        except Exception as e:
            print(e)
            return {
                "statusCode": 400,
                "body": f"❌ {e}",
            }

        return {
            "statusCode": 200,
            "body": f"📊 Product Performance: {performance_data}",
        }

    return {
        "statusCode": 400,
        "body": f"❌ Unknown toolname: {resource}",
    }
