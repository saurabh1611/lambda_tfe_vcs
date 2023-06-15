import requests
import time

def trigger_terraform_plan(api_token, organization, workspace):
    # Specify the Terraform Enterprise base URL
    base_url = 'https://app.terraform.io/api/v2/runs'

    # Set the request headers
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/vnd.api+json'
    }

    # Set the request body
    payload = {
      "data": {
        "attributes": {
          "message": "Infra Provisioning - Plan",
          "plan-only": "false",
          "is-destroy": "false",
          "auto-apply": "true"
        },
        "type":"runs",
        "relationships": {
          "workspace": {
            "data": {
              "type": "workspaces",
              "id": "ws-rHYzeJCNtPxQu12h"
            }
          }
        }
      }
    }


    try:
        # Make the API call
        response = requests.post(base_url, json=payload, headers=headers)

        # Check the response status code
        if response.status_code == 201:
            # API call was successful
            data = response.json()
            run_id = data['data']['id']
            print(f"Plan triggered successfully. Run ID: {run_id}")
            return run_id
        else:
            # API call failed
            print(f"Failed to trigger plan. Status code: {response.status_code}")
            print(response.text)
            return run_id
    except requests.exceptions.RequestException as e:
        print("Error occurred during plan API call:")
        print(str(e))
        return null

def trigger_terraform_apply(api_token, organization, workspace, plan_run_id):
    # Specify the Terraform Enterprise base URL
    base_url = 'https://app.terraform.io/api/v2/runs/' + plan_run_id + '/actions/apply'
    # print(base_url)

    # Set the request headers
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/vnd.api+json'
    }

    # Set the request body
    payload = {
      "comment":"Plan auto approved"
    }

    try:
        # Make the API call
        response = requests.post(base_url, json=payload, headers=headers)

        # Check the response status code
        if response.status_code == 201:
            # API call was successful
            # data = response.json()
            # run_id = data['data']['id']
            print(f"Apply triggered successfully. Run ID: {run_id}")
        else:
            # API call failed
            print(f"Failed to trigger apply. Status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print("Error occurred during apply API call:")
        print(str(e))
        
def fetch_terraform_run_status(api_token, organization, workspace, plan_run_id):
    # Specify the Terraform Enterprise base URL
    base_url = 'https://app.terraform.io/api/v2/runs/' + plan_run_id

    # Set the request headers
    headers = {
        'Authorization': f'Bearer {api_token}',
    }

    try:
        while True:
            # Make the API call
            response = requests.get(base_url, headers=headers)
            # print(response)
    
            # Check the response status code
            if response.status_code == 200:
                # API call was successful
                data = response.json()
                run_status = data['data']['attributes']['status']
                print(run_status)
                if run_status == 'pending' or run_status == 'plan_queued' or run_status == 'planning' :
                    # Plan is still in progress, wait for a few seconds before checking again
                    print("Plan is still in progress. Checking again in 5 seconds...")
                    time.sleep(10)
                elif run_status == 'planned_and_finished':
                    # Plan and cost estimation completed successfully
                    print(f"Plan completed successfully. Run ID: {plan_run_id}")
                    return 'planned_and_finished'
                elif run_status == 'applied':
                    # Applied completed successfully
                    print(f"Apply completed successfully. Run ID: {plan_run_id}")
                    return 'applied'
                elif run_status == 'errored':
                    # Plan failed or encountered an error
                    print(f"Plan failed or encountered an error. Run ID: {plan_run_id}")
                    return 'errored'
                else:
                    print(f"Waiting to fetch the run status")
            else:
                # API call failed
                print(f"Failed to fetch run status. Status code: {response.status_code}")
                print(response.text)
                return 'api_failed'
    except requests.exceptions.RequestException as e:
        print("Error occurred during plan API call:")
        print(str(e))

def lambda_handler(event, context):
    api_token = "mxlIwmavmot0Ig.atlasv1.nEtyzUW70RG7zsCvUth2XeOyypaoXNhWsLNoHt2QIrf3Tft2Jf9GUfFXCc5zYIQg5D0"
    organization = "rizwan-poc"
    workspace = "instancecreation-tfe"
    
    plan_run_id = trigger_terraform_plan(api_token, organization, workspace)
    
    run_status = fetch_terraform_run_status(api_token, organization, workspace, plan_run_id)
    
    # run_status = "demo"
    
    if plan_run_id == "null" or run_status == 'api_failed' or run_status == 'errored':
        print("Error occurred during API call")
    else:
        trigger_terraform_apply(api_token, organization, workspace, plan_run_id)
