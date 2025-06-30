import React from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Typography,
} from '@mui/material';
import { useQuery } from '@tanstack/react-query';
import { loadStripe } from '@stripe/stripe-js';
import { api } from '../services/api';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY || '');

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  image?: string;
}

export default function Products() {
  const { data: products, isLoading } = useQuery<Product[]>({
    queryKey: ['products'],
    queryFn: () => api.get('/products').then((res) => res.data),
  });

  const handleBuyNow = async (productId: string) => {
    try {
      const stripe = await stripePromise;
      if (!stripe) throw new Error('Stripe failed to initialize');

      const response = await api.post('/payment/create-checkout-session', {
        productId,
      });

      const result = await stripe.redirectToCheckout({
        sessionId: response.data.sessionId,
      });

      if (result.error) {
        console.error(result.error);
      }
    } catch (error) {
      console.error('Payment error:', error);
    }
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Products
      </Typography>
      <Grid container spacing={3}>
        {products?.map((product) => (
          <Grid item xs={12} sm={6} md={4} key={product.id}>
            <Card>
              {product.image && (
                <Box
                  component="img"
                  sx={{
                    height: 200,
                    width: '100%',
                    objectFit: 'cover',
                  }}
                  src={product.image}
                  alt={product.name}
                />
              )}
              <CardContent>
                <Typography gutterBottom variant="h5" component="div">
                  {product.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {product.description}
                </Typography>
                <Typography variant="h6" color="primary" sx={{ mt: 2 }}>
                  ${product.price}
                </Typography>
              </CardContent>
              <CardActions>
                <Button
                  size="small"
                  variant="contained"
                  onClick={() => handleBuyNow(product.id)}
                >
                  Buy Now
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
} 