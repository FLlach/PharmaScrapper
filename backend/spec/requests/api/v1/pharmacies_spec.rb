require 'swagger_helper'

RSpec.describe 'api/v1/pharmacies', type: :request do
  path '/api/v1/pharmacies' do
    get('list pharmacies') do
      tags 'Pharmacies'
      produces 'application/json'

      response(200, 'successful') do
        schema type: :array, items: {
          type: :object,
          properties: {
            id: { type: :integer },
            name: { type: :string },
            base_domain: { type: :string },
            logo_url: { type: :string },
            active: { type: :boolean }
          }
        }
        run_test!
      end
    end
  end
end
