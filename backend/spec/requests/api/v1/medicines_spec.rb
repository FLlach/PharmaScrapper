require 'swagger_helper'

RSpec.describe 'api/v1/medicines', type: :request do
  path '/api/v1/medicines' do
    get('list medicines') do
      tags 'Medicines'
      produces 'application/json'
      parameter name: :query, in: :query, type: :string, description: 'Search query for medicine name or active ingredient', required: false

      response(200, 'successful') do
        let!(:medicine) { Medicine.create(name: 'Test Medicine') }
        let(:id) { medicine.id }
        schema type: :array, items: {
          type: :object,
          properties: {
            id: { type: :integer },
            name: { type: :string },
            active_ingredient: { type: :string, nullable: true },
            dosage: { type: :string, nullable: true },
            bioequivalent: { type: :boolean, nullable: true }
          }
        }
        run_test!
      end
    end
  end

  path '/api/v1/medicines/{id}/comparison' do
    get('compare medicine prices') do
      tags 'Medicines'
      produces 'application/json'
      let(:id) { '123' }; parameter name: 'id', in: :path, type: :string, description: 'id'

      response(200, 'successful') do
        let!(:medicine) { Medicine.create(name: 'Test Medicine') }
        let(:id) { medicine.id }
        schema type: :object, properties: {
          medicine: {
            type: :object,
            properties: {
              id: { type: :integer },
              name: { type: :string }
            }
          },
          comparisons: {
            type: :array,
            items: {
              type: :object,
              properties: {
                pharmacy: { type: :string },
                pharmacy_logo: { type: :string, nullable: true },
                product_name: { type: :string },
                sku: { type: :string },
                url: { type: :string },
                image_url: { type: :string, nullable: true },
                current_price_regular: { type: :integer, nullable: true },
                current_price_offer: { type: :integer, nullable: true },
                in_stock: { type: :boolean },
                last_captured_at: { type: :string, format: 'date-time' }
              }
            }
          }
        }
        run_test!
      end
    end
  end
end
